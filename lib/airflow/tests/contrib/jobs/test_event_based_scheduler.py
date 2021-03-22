# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import os
import pickle
import sqlalchemy
import time
import unittest
from typing import List

import psutil
from airflow.models.taskexecution import TaskExecution
from notification_service.base_notification import BaseEvent, UNDEFINED_EVENT_TYPE
from notification_service.client import NotificationClient
from notification_service.event_storage import MemoryEventStorage
from notification_service.master import NotificationMaster
from notification_service.service import NotificationService

from airflow.contrib.jobs.event_based_scheduler_job import EventBasedSchedulerJob, SchedulerEventWatcher, \
    EventBasedScheduler
from airflow.executors.local_executor import LocalExecutor
from airflow.models import TaskInstance, Message
from airflow.jobs.base_job import BaseJob
from airflow.utils.mailbox import Mailbox
from airflow.utils.session import create_session, provide_session
from airflow.events.scheduler_events import StopSchedulerEvent
from tests.test_utils import db

TEST_DAG_FOLDER = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, 'dags')


class TestEventBasedScheduler(unittest.TestCase):

    def setUp(self):
        db.clear_db_jobs()
        db.clear_db_dags()
        db.clear_db_serialized_dags()
        db.clear_db_runs()
        db.clear_db_task_execution()
        db.clear_db_message()
        self.scheduler = None
        self.port = 50101
        self.storage = MemoryEventStorage()
        self.master = NotificationMaster(NotificationService(self.storage), self.port)
        self.master.run()
        self.client = NotificationClient(server_uri="localhost:{}".format(self.port),
                                         default_namespace="test_namespace")

    def tearDown(self):
        self.master.stop()

    def test_event_based_scheduler(self):
        import time
        pid = os.fork()
        if pid == 0:
            try:
                ppid = os.fork()
                if ppid == 0:
                    # Fork twice to avoid the sleeping in main process block scheduler
                    self.start_scheduler("../../dags/test_event_based_scheduler.py")
            except Exception as e:
                print("Failed to execute task %s.", str(e))
        else:
            try:
                self.wait_for_task("event_based_scheduler_dag", "sleep_1000_secs", "running")
                print("Waiting for task starting")
                time.sleep(20)
                self.send_event("stop")
                self.wait_for_task("event_based_scheduler_dag", "sleep_1000_secs", "killed")
                tes: List[TaskExecution] = self.get_task_execution("event_based_scheduler_dag", "python_sleep")
                self.assertEqual(len(tes), 1)
                self.send_event("any_key")
                self.wait_for_task_execution("event_based_scheduler_dag", "python_sleep", 2)
                self.wait_for_task("event_based_scheduler_dag", "python_sleep", "running")
            finally:
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                    child.kill()
                parent.kill()

    def test_replay_message(self):
        key = "stop"
        mailbox = Mailbox()
        mailbox.set_scheduling_job_id(1234)
        watcher = SchedulerEventWatcher(mailbox)
        self.client.start_listen_events(
            watcher=watcher,
            start_time=int(time.time() * 1000),
            version=None
        )
        self.send_event(key)
        msg: BaseEvent = mailbox.get_message()
        self.assertEqual(msg.key, key)
        with create_session() as session:
            msg_from_db = session.query(Message).first()
            expect_non_unprocessed = EventBasedScheduler.get_unprocessed_message(1000)
            self.assertEqual(0, len(expect_non_unprocessed))
            unprocessed = EventBasedScheduler.get_unprocessed_message(1234)
            self.assertEqual(unprocessed[0].serialized_message, msg_from_db.data)
        deserialized_data = pickle.loads(msg_from_db.data)
        self.assertEqual(deserialized_data.key, key)
        self.assertEqual(msg, deserialized_data)

    def send_event(self, key):
        event = self.client.send_event(BaseEvent(key=key,
                                                 event_type=UNDEFINED_EVENT_TYPE,
                                                 value="value1"))
        self.assertEqual(key, event.key)

    @provide_session
    def get_task_execution(self, dag_id, task_id, session):
        return session.query(TaskExecution).filter(TaskExecution.dag_id == dag_id,
                                                   TaskExecution.task_id == task_id).all()

    @provide_session
    def get_latest_job_id(self, session):
        return session.query(BaseJob).order_by(sqlalchemy.desc(BaseJob.id)).first().id

    def start_scheduler(self, file_path):
        self.scheduler = EventBasedSchedulerJob(
            dag_directory=file_path,
            server_uri="localhost:{}".format(self.port),
            executor=LocalExecutor(3),
            max_runs=-1,
            refresh_dag_dir_interval=30
        )
        print("scheduler starting")
        self.scheduler.run()

    def wait_for_task_execution(self, dag_id, task_id, expected_num):
        result = False
        check_nums = 100
        while check_nums > 0:
            time.sleep(2)
            check_nums = check_nums - 1
            tes = self.get_task_execution(dag_id, task_id)
            if len(tes) == expected_num:
                result = True
                break
        self.assertTrue(result)

    def wait_for_task(self, dag_id, task_id, expected_state):
        result = False
        check_nums = 100
        while check_nums > 0:
            time.sleep(2)
            check_nums = check_nums - 1
            with create_session() as session:
                ti = session.query(TaskInstance).filter(
                    TaskInstance.dag_id == dag_id,
                    TaskInstance.task_id == task_id
                ).first()
            if ti and ti.state == expected_state:
                result = True
                break
        self.assertTrue(result)

    def test_notification(self):
        self.client.send_event(BaseEvent(key='a', value='b'))

    def run_a_task_function(self):
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'single',
                                                          TaskExecution.task_id == 'task_1').all()
                if len(tes) > 0:
                    break
                else:
                    time.sleep(1)
        self.client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_run_a_task(self):
        import threading
        t = threading.Thread(target=self.run_a_task_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler('../../dags/test_single_task_dag.py')
        tes: List[TaskExecution] = self.get_task_execution("single", "task_1")
        self.assertEqual(len(tes), 1)

    def run_event_task_function(self):
        client = NotificationClient(server_uri="localhost:{}".format(self.port),
                                    default_namespace="test_namespace")
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'event_dag',
                                                          TaskExecution.task_id == 'task_1').all()
                if len(tes) > 0:
                    client.send_event(BaseEvent(key='start', value='', namespace=''))
                    while True:
                        tes_2 = session.query(TaskExecution).filter(TaskExecution.dag_id == 'event_dag',
                                                                    TaskExecution.task_id == 'task_2').all()
                        if len(tes_2) > 0:
                            break
                        else:
                            time.sleep(1)
                    break
                else:
                    time.sleep(1)
        client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_run_event_task(self):
        import threading
        t = threading.Thread(target=self.run_event_task_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler('../../dags/test_event_task_dag.py')
        tes: List[TaskExecution] = self.get_task_execution("event_dag", "task_2")
        self.assertEqual(len(tes), 1)
