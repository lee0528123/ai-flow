/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package org.aiflow.notification.client;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import com.speedment.common.tuple.Tuple4;
import com.speedment.common.tuple.internal.nonnullable.Tuple4Impl;
import io.grpc.ManagedChannelBuilder;
import org.aiflow.notification.conf.Configuration;
import org.aiflow.notification.entity.EventMeta;
import org.aiflow.notification.entity.SenderEventCount;
import org.aiflow.notification.proto.NotificationServiceGrpc;
import org.aiflow.notification.proto.NotificationServiceOuterClass;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

import static org.aiflow.notification.conf.Configuration.CLIENT_ENABLE_IDEMPOTENCE_CONFIG_DEFAULT_VALUE;
import static org.aiflow.notification.conf.Configuration.CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY;
import static org.aiflow.notification.conf.Configuration.CLIENT_ID_CONFIG_DEFAULT_VALUE;
import static org.aiflow.notification.conf.Configuration.CLIENT_ID_CONFIG_KEY;
import static org.aiflow.notification.conf.Configuration.CLIENT_INITIAL_SEQUENCE_NUMBER_CONFIG_DEFAULT_VALUE;
import static org.aiflow.notification.conf.Configuration.CLIENT_INITIAL_SEQUENCE_NUMBER_CONFIG_KEY;

public class NotificationClient {

    private static final Logger logger = LoggerFactory.getLogger(NotificationClient.class);
    public static String ANY_CONDITION = "*";
    private static final String SERVER_URI = "localhost:50051";
    private final String defaultNamespace;
    private final Integer listMemberIntervalMs;
    private final Integer retryIntervalMs;
    private final Integer retryTimeoutMs;
    private final Map<Tuple4<String, String, String, String>, EventListener>
            threads; // key, namespace, event_type, sender
    private final ExecutorService listMembersService;
    private NotificationServiceGrpc.NotificationServiceBlockingStub notificationServiceStub;
    private Set<NotificationServiceOuterClass.MemberProto> livingMembers;
    private Boolean enableHa;
    private String currentUri;
    private String sender;
    private Long clientId;
    private AtomicInteger sequenceNum;
    private final Configuration conf;

    public NotificationClient(
            String target,
            String defaultNamespace,
            String sender,
            Boolean enableHa,
            Integer listMemberIntervalMs,
            Integer retryIntervalMs,
            Integer retryTimeoutMs,
            Properties properties)
            throws Exception {
        this.defaultNamespace = defaultNamespace;
        this.sender = sender;
        this.enableHa = enableHa;
        this.listMemberIntervalMs = listMemberIntervalMs;
        this.retryIntervalMs = retryIntervalMs;
        this.retryTimeoutMs = retryTimeoutMs;
        this.conf = new Configuration(properties);

        if (enableHa) {
            String[] serverUris = StringUtils.split(target, ",");
            boolean lastError = true;
            for (String serverUri : serverUris) {
                currentUri = serverUri;
                try {
                    initNotificationServiceStub();
                    lastError = false;
                    break;
                } catch (Exception e) {
                    continue;
                }
            }
            if (lastError) {
                logger.warn("Failed to initialize client");
            }
        } else {
            currentUri = target;
            initNotificationServiceStub();
        }

        boolean enableIdempotence =
                this.conf.getBoolean(
                        CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY,
                        CLIENT_ENABLE_IDEMPOTENCE_CONFIG_DEFAULT_VALUE);
        long clientId = this.conf.getLong(CLIENT_ID_CONFIG_KEY, CLIENT_ID_CONFIG_DEFAULT_VALUE);
        int initialSeqNum =
                this.conf.getInt(
                        CLIENT_INITIAL_SEQUENCE_NUMBER_CONFIG_KEY,
                        CLIENT_INITIAL_SEQUENCE_NUMBER_CONFIG_DEFAULT_VALUE);
        if (enableIdempotence) {
            initNotificationServiceStub();
            if (clientId < 0) {
                this.clientId = registerClient();
            } else {
                if (checkClientExists(clientId)) {
                    this.clientId = clientId;
                } else {
                    throw new Exception(
                            "Init notification client with a client id which have not registered.");
                }
            }
            this.sequenceNum = new AtomicInteger(initialSeqNum);
        }

        threads = new HashMap<>();
        livingMembers = new HashSet<>();
        listMembersService =
                Executors.newSingleThreadExecutor(
                        new ThreadFactoryBuilder()
                                .setDaemon(true)
                                .setNameFormat("list-members-%d")
                                .build());
        listMembersService.submit(listMembers());
    }

    /**
     * *
     *
     * @return Id of registered client
     */
    private long registerClient() throws Exception {
        NotificationServiceOuterClass.RegisterClientRequest registerClientRequest =
                NotificationServiceOuterClass.RegisterClientRequest.newBuilder()
                        .setClientMeta(
                                NotificationServiceOuterClass.ClientMeta.newBuilder()
                                        .setNamespace(defaultNamespace)
                                        .setSender(sender)
                                        .build())
                        .build();
        NotificationServiceOuterClass.RegisterClientResponse registerClientResponse =
                notificationServiceStub.registerClient(registerClientRequest);
        if (registerClientResponse.getReturnCode()
                == NotificationServiceOuterClass.ReturnStatus.SUCCESS) {
            return registerClientResponse.getClientId();
        } else {
            throw new Exception(registerClientResponse.getReturnMsg());
        }
    }

    private boolean checkClientExists(long clientId) {
        NotificationServiceOuterClass.ClientIdRequest request =
                NotificationServiceOuterClass.ClientIdRequest.newBuilder()
                        .setClientId(clientId)
                        .build();
        NotificationServiceOuterClass.isClientExistsResponse response =
                notificationServiceStub.isClientExists(request);
        if (response.getReturnCode() == NotificationServiceOuterClass.ReturnStatus.SUCCESS
                && response.getIsExists()) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * List specific registered listener events in Notification Service.
     *
     * @param serviceStub Notification service GRPC stub.
     * @param namespace The namespace of the event.
     * @param sender The sender of the event.
     * @param keys Keys of event for listening.
     * @param version (Optional) Version of event for listening.
     * @param eventType The event type of the event.
     * @param startTime Events generated after this time.
     * @param timeoutSeconds List events request timeout seconds.
     * @return List of event updated in Notification Service.
     */
    protected static List<EventMeta> listEvents(
            NotificationServiceGrpc.NotificationServiceBlockingStub serviceStub,
            String namespace,
            String sender,
            List<String> keys,
            long version,
            String eventType,
            long startTime,
            Integer timeoutSeconds)
            throws Exception {
        NotificationServiceOuterClass.ListEventsRequest request =
                NotificationServiceOuterClass.ListEventsRequest.newBuilder()
                        .addAllKeys(keys)
                        .setStartVersion(version)
                        .setEventType(eventType)
                        .setStartTime(startTime)
                        .setNamespace(namespace)
                        .setSender(sender)
                        .setTimeoutSeconds(timeoutSeconds)
                        .build();
        return parseEventsFromResponse(serviceStub.listEvents(request));
    }

    private static List<EventMeta> parseEventsFromResponse(
            NotificationServiceOuterClass.ListEventsResponse response) throws Exception {
        if (response.getReturnCode() == NotificationServiceOuterClass.ReturnStatus.SUCCESS) {
            List<EventMeta> eventMetas = new ArrayList<>();
            for (NotificationServiceOuterClass.EventProto eventProto : response.getEventsList()) {
                eventMetas.add(EventMeta.buildEventMeta(eventProto));
            }
            return eventMetas;
        } else {
            throw new Exception(response.getReturnMsg());
        }
    }

    private static ImmutablePair<Long, List<SenderEventCount>> parseEventCountFromResponse(
            NotificationServiceOuterClass.CountEventsResponse response) throws Exception {
        if (response.getReturnCode() == NotificationServiceOuterClass.ReturnStatus.SUCCESS) {
            List<SenderEventCount> senderEventCounts = new ArrayList<>();
            for (NotificationServiceOuterClass.SenderEventCountProto eventCountProto :
                    response.getSenderEventCountsList()) {
                senderEventCounts.add(SenderEventCount.buildSenderEventCount(eventCountProto));
            }
            return new ImmutablePair<>(response.getEventCount(), senderEventCounts);
        } else {
            throw new Exception(response.getReturnMsg());
        }
    }

    protected static NotificationServiceGrpc.NotificationServiceBlockingStub wrapBlockingStub(
            NotificationServiceGrpc.NotificationServiceBlockingStub stub,
            String target,
            Set<NotificationServiceOuterClass.MemberProto> livingMembers,
            Boolean haRunning,
            Integer retryIntervalMs,
            Integer retryTimeoutMs) {
        return NotificationServiceGrpc.newBlockingStub(
                        ManagedChannelBuilder.forTarget(target).usePlaintext().build())
                .withInterceptors(
                        new NotificationInterceptor(
                                stub,
                                target,
                                livingMembers,
                                haRunning,
                                retryIntervalMs,
                                retryTimeoutMs));
    }

    /** Initialize notification service stub. */
    protected void initNotificationServiceStub() {
        if (notificationServiceStub == null) {
            notificationServiceStub =
                    NotificationServiceGrpc.newBlockingStub(
                            ManagedChannelBuilder.forTarget(
                                            StringUtils.isEmpty(currentUri)
                                                    ? SERVER_URI
                                                    : currentUri)
                                    .usePlaintext()
                                    .build());
        }
        if (enableHa) {
            notificationServiceStub =
                    wrapBlockingStub(
                            notificationServiceStub,
                            StringUtils.isEmpty(currentUri) ? SERVER_URI : currentUri,
                            livingMembers,
                            enableHa,
                            retryIntervalMs,
                            retryTimeoutMs);
        }
    }

    /** Select a valid server from server candidates as current server. */
    protected void selectValidServer() {
        boolean lastError = false;
        for (NotificationServiceOuterClass.MemberProto livingMember : livingMembers) {
            try {
                currentUri = livingMember.getServerUri();
                initNotificationServiceStub();
                NotificationServiceOuterClass.ListMembersRequest request =
                        NotificationServiceOuterClass.ListMembersRequest.newBuilder()
                                .setTimeoutSeconds(listMemberIntervalMs / 1000)
                                .build();
                NotificationServiceOuterClass.ListMembersResponse response =
                        notificationServiceStub.listMembers(request);
                if (response.getReturnCode()
                        == NotificationServiceOuterClass.ReturnStatus.SUCCESS) {
                    livingMembers = new HashSet<>(response.getMembersList());
                    lastError = false;
                    break;
                } else {
                    lastError = true;
                }
            } catch (Exception e) {
                lastError = true;
            }
        }
        if (lastError) {
            logger.warn("No available server uri!");
        }
    }

    /** List living members under high available mode. */
    protected Runnable listMembers() {
        return () -> {
            while (enableHa) {
                try {
                    if (Thread.currentThread().isInterrupted()) {
                        break;
                    }
                    NotificationServiceOuterClass.ListMembersRequest request =
                            NotificationServiceOuterClass.ListMembersRequest.newBuilder()
                                    .setTimeoutSeconds(listMemberIntervalMs / 1000)
                                    .build();
                    NotificationServiceOuterClass.ListMembersResponse response =
                            notificationServiceStub.listMembers(request);
                    if (response.getReturnCode()
                            == NotificationServiceOuterClass.ReturnStatus.SUCCESS) {
                        livingMembers = new HashSet<>(response.getMembersList());
                    } else {
                        logger.warn(response.getReturnMsg());
                        selectValidServer();
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    logger.warn("Error while listening notification");
                    selectValidServer();
                }
            }
        };
    }

    /** Disable high availability mode. */
    public void disableHighAvailability() {
        enableHa = false;
        listMembersService.shutdown();
    }

    /**
     * Send the event to Notification Service.
     *
     * @param key Key of event updated in Notification Service.
     * @param value Value of event updated in Notification Service.
     * @param eventType Type of event updated in Notification Service.
     * @param context Context of event updated in Notification Service.
     * @return Object of Event created in Notification Service.
     */
    public EventMeta sendEvent(String key, String value, String eventType, String context)
            throws Exception {
        boolean enableIdempotence =
                this.conf.getBoolean(
                        CLIENT_ENABLE_IDEMPOTENCE_CONFIG_KEY,
                        CLIENT_ENABLE_IDEMPOTENCE_CONFIG_DEFAULT_VALUE);
        String signature = UUID.randomUUID().toString();
        if (enableIdempotence) {
            int currentSeqNum = this.sequenceNum.get();
            signature =
                    StringUtils.join(Arrays.asList("client", this.clientId, currentSeqNum), "_");
        }
        NotificationServiceOuterClass.SendEventRequest request =
                NotificationServiceOuterClass.SendEventRequest.newBuilder()
                        .setEvent(
                                NotificationServiceOuterClass.EventProto.newBuilder()
                                        .setKey(key)
                                        .setValue(value)
                                        .setEventType(eventType)
                                        .setContext(context)
                                        .setNamespace(defaultNamespace)
                                        .setSender(sender)
                                        .build())
                        .setUuid(signature)
                        .setEnableIdempotence(enableIdempotence)
                        .build();
        NotificationServiceOuterClass.SendEventsResponse response =
                notificationServiceStub.sendEvent(request);
        if (response.getReturnCode() == NotificationServiceOuterClass.ReturnStatus.SUCCESS) {
            if (enableIdempotence) {
                this.sequenceNum.getAndIncrement();
            }
            return EventMeta.buildEventMeta(response.getEvent());
        } else {
            throw new Exception(response.getReturnMsg());
        }
    }

    /**
     * List specific `key` or `version` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param sender The sender of the event.
     * @param keys Keys of notification for listening.
     * @param version (Optional) Version of notification for listening.
     * @param eventType (Optional) Type of event for listening.
     * @param startTime (Optional) Type of event for listening.
     * @return List of Notification updated in Notification Service.
     */
    public List<EventMeta> listEvents(
            String namespace,
            List<String> keys,
            long version,
            String eventType,
            long startTime,
            String sender)
            throws Exception {
        return listEvents(
                notificationServiceStub,
                StringUtils.isEmpty(namespace) ? defaultNamespace : namespace,
                sender,
                keys,
                version,
                eventType,
                startTime,
                0);
    }

    /**
     * Count specific `key` or `version` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param sender The sender of the event.
     * @param keys Keys of notification for listening.
     * @param version (Optional) Version of notification for listening.
     * @param eventType (Optional) Type of event for listening.
     * @param startTime (Optional) Type of event for listening.
     * @return Count of Notification updated in Notification Service.
     */
    public ImmutablePair<Long, List<SenderEventCount>> countEvents(
            String namespace,
            List<String> keys,
            long version,
            String eventType,
            long startTime,
            String sender)
            throws Exception {
        NotificationServiceOuterClass.CountEventsRequest request =
                NotificationServiceOuterClass.CountEventsRequest.newBuilder()
                        .addAllKeys(keys)
                        .setStartVersion(version)
                        .setEventType(eventType)
                        .setStartTime(startTime)
                        .setNamespace(StringUtils.isEmpty(namespace) ? defaultNamespace : namespace)
                        .setSender(sender)
                        .build();
        return parseEventCountFromResponse(notificationServiceStub.countEvents(request));
    }

    /**
     * List all registered listener events in Notification Service.
     *
     * @param startTime (Optional) The event create time after the given startTime.
     * @param startVersion (Optional) Start version of event for listening.
     * @param endVersion (Optional) End version of event for listening.
     * @return List of event updated in Notification Service.
     */
    public List<EventMeta> listAllEvents(long startTime, long startVersion, long endVersion)
            throws Exception {
        NotificationServiceOuterClass.ListAllEventsRequest request =
                NotificationServiceOuterClass.ListAllEventsRequest.newBuilder()
                        .setStartTime(startTime)
                        .setStartVersion(startVersion)
                        .setEndVersion(endVersion)
                        .build();
        NotificationServiceOuterClass.ListEventsResponse response =
                notificationServiceStub.listAllEvents(request);
        return parseEventsFromResponse(response);
    }

    /**
     * Start listen specific `key` or `version` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param key Key of notification for listening.
     * @param watcher Watcher instance for listening notification.
     * @param version (Optional) Version of notification for listening.
     * @param eventType (Optional) Type of event for listening.
     * @param startTime (Optional) Type of event for listening.
     * @param sender The sender of the event.
     */
    public void startListenEvent(
            String namespace,
            String key,
            EventWatcher watcher,
            long version,
            String eventType,
            long startTime,
            String sender) {
        String realNamespace = StringUtils.isEmpty(namespace) ? ANY_CONDITION : namespace;
        String realKey = StringUtils.isEmpty(key) ? ANY_CONDITION : key;
        String realEventType = StringUtils.isEmpty(eventType) ? ANY_CONDITION : eventType;
        String realSender = StringUtils.isEmpty(sender) ? ANY_CONDITION : sender;

        Tuple4<String, String, String, String> listenKey =
                new Tuple4Impl<>(realKey, realNamespace, realEventType, realSender);
        if (!threads.containsKey(listenKey)) {
            ArrayList<String> curListenerKeys =
                    new ArrayList<String>() {
                        {
                            add(realKey);
                        }
                    };
            EventListener listener =
                    new EventListener(
                            notificationServiceStub,
                            curListenerKeys,
                            version,
                            realEventType,
                            startTime,
                            realNamespace,
                            realSender,
                            watcher,
                            5);
            listener.start();
            threads.put(listenKey, listener);
        }
    }

    /**
     * Stop listen specific `key` notifications in Notification Service.
     *
     * @param namespace The namespace of the event.
     * @param key The key of the event.
     * @param eventType The event type of the event.
     * @param sender The sender of the event.
     */
    public void stopListenEvent(String namespace, String key, String eventType, String sender) {
        String realNamespace = StringUtils.isEmpty(namespace) ? ANY_CONDITION : namespace;
        String realKey = StringUtils.isEmpty(key) ? ANY_CONDITION : key;
        String realEventType = StringUtils.isEmpty(eventType) ? ANY_CONDITION : eventType;
        String realSender = StringUtils.isEmpty(sender) ? ANY_CONDITION : sender;

        Tuple4<String, String, String, String> listenKey =
                new Tuple4Impl<>(realKey, realNamespace, realEventType, realSender);

        if (threads.containsKey(listenKey)) {
            threads.get(listenKey).shutdown();
            threads.remove(listenKey);
        }
    }

    /**
     * Get latest version of specific `key` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param key Key of notification for listening.
     */
    public long getLatestVersion(String namespace, String key) throws Exception {
        if (StringUtils.isEmpty(key)) {
            throw new Exception("Empty key, please provide valid key");
        } else {
            NotificationServiceOuterClass.GetLatestVersionByKeyRequest request =
                    NotificationServiceOuterClass.GetLatestVersionByKeyRequest.newBuilder()
                            .setNamespace(
                                    StringUtils.isEmpty(namespace) ? defaultNamespace : namespace)
                            .setKey(key)
                            .build();
            NotificationServiceOuterClass.GetLatestVersionResponse response =
                    notificationServiceStub.getLatestVersionByKey(request);
            return parseLatestVersionFromResponse(response);
        }
    }

    public long parseLatestVersionFromResponse(
            NotificationServiceOuterClass.GetLatestVersionResponse response) throws Exception {
        if (response.getReturnCode()
                .equals(NotificationServiceOuterClass.ReturnStatus.ERROR.toString())) {
            throw new Exception(response.getReturnMsg());
        } else {
            return response.getVersion();
        }
    }

    public AtomicInteger getSequenceNum() {
        return this.sequenceNum;
    }

    public Long getClientId() {
        return clientId;
    }

    public void close() throws Exception {
        if (this.clientId >= 0) {
            NotificationServiceOuterClass.ClientIdRequest request =
                    NotificationServiceOuterClass.ClientIdRequest.newBuilder()
                            .setClientId(this.clientId)
                            .build();
            NotificationServiceOuterClass.CommonResponse response =
                    notificationServiceStub.deleteClient(request);
            if (response.getReturnCode() != NotificationServiceOuterClass.ReturnStatus.SUCCESS) {
                throw new Exception(response.getReturnMsg());
            }
        }
    }
}
