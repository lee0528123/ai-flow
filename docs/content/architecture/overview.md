# Overview

## Introduction

AIFlow is an open source platform to manage the machine learning lifecycle, including feature engineering, 
model training, model evaluation, model serving, model inference, metric monitoring, etc.

## Architecture
 
The overall architecture of AIFlow is shown in the figure blew:

![Alt text](../images/architecture/architecture.png)

AIFlow consists of components: AIFlow SDK, AIFlow Server, Notification Server, Scheduler.

1. __SDK__: AIFlow SDK provides the API of workflow operation and the client of the Meta Service and Scheduler Service.
   The SDK consists of four parts: AIFlow API, AI Graph, Translator and Workflow.
   
    * __AIFlow API__:  AIFlow API provides the functions like defining a machine learning workflow,
      controlling workflow  (submit, run, stop, etc.), sending/listening event, managing meta-information 
      and developing plugins.

    * __AI Graph__: AI Graph is a logical calculation graph generated by the user-defined AIFlow program. 
      
      AI Nodes, Data Edges and Control Edges compose AI Graph.
      
      * AI Node: It defines the calculation logic in the machine learning process. 
      
      * Data Edge: It defines the data dependency between AI Nodes.
      
      * Control Edge: It describes the event trigger conditions for controlling Job.
      
    * __Workflow__: Workflow defines a set of execution rules for Jobs.
      
      Jobs and Control Edges compose the Workflow. 
      
      * Job: It is a description of an executable unit converted from a set of AI Nodes with the same job configuration. 
      
      * Control Edge: It describes the event trigger conditions for controlling Job.
      
    * __Translator__: The role of the Translator is to translate the AI Graph defined by the AIFlow program 
      into a Workflow.
   
2. __AIFlow Server__: AIFlow Server provides meta information management and scheduling services.
   * __Meta Service__: Meta service is responsible for managing meta information of AIFlow projects. 
     The metas in Meta Service include the meta of the dataset, model, project, workflow, artifact and metric.
     
   * __Scheduling Service__: Scheduling Service is responsible for processing requests to submit workflow, 
     run workflow, stop workflow, etc.

3. __Notification Server__: Notification Server provides notification service which support the event publishing and subscription.

4. __Scheduler__: Scheduler provides the function of executing workflow.

## Principle

The figure below shows the principle of AIFlow:

![Alt text](../images/architecture/principle.png)

1. AI Graph represents the user-defined AIFlow program.
2. Translates AI Graph to a Workflow that can be managed by Scheduler Service.
3. Client submits Workflow to Scheduling Service.
4. Scheduling Service calls scheduler to execute workflow.   
5. User programs can register meta information.
6. When the Scheduler runs the workflow, 
   it will send events to Notification Server and listen to the events from Notification Server.
7. Meta Service sends events to Notification Server, such as model version generation events, etc.
8. User programs can also send events to Notification Server or listen to events from Notification Server.

## SDK
SDK is provided by AIFlow to develop the AIFlow programs.
The following section explains in detail the functions included in the SDK.

### AIFlow API

AIFlow API is the interface provided by AIFlow to users.
AIFlow API mainly includes 4 categories:
1. Definition of machine workflow:
   Users can define the workflow of a machine learning project.
2. Meta-information addition, deletion and modification:
   Users can manage meta-information, such as project meta-information, data meta-information, model meta-information, etc.
3. Machine learning workflow life cycle management:
   Users can manage machine learning workflows, such as submitting workflows, running workflows, stopping workflows, etc.
4. Plugin extension:
   Users can extend through the plugin interface. 
   The functions that support extensions are: JobPlugin, Scheduler and BlobManager. 
   The plugin will be explained in detail later.
   

### AI Graph

AI Graph: As shown in the figure below, it consists of AI Node, Data Edge and Control Edge . 

![Alt text](../images/architecture/ai_graph.png)

1. AI Node: It defines a type of machine learning logical operation, such as transformation, training etc.
   A Job Config is associated with a group of AI Nodes, and the AI Nodes in a group can only be connected by the DataEdges.
2. Data Edge: The Data Edge connects two AI Nodes, 
   indicating that the downstream AI Node depends on the data produced by the upstream AI Node.
3. Control Edge：Control Edge represents the condition under which a job action should be triggered. 
   The events that trigger the job action can come from the job in the same workflow or from an external system.


### Workflow

Workflow defines a set of execution rules for Jobs.

Jobs and Control Edges make up a Workflow.

![Alt text](../images/architecture/workflow.png)

1. Job：It is the unit that the scheduler can run.
2. Control edge: It represents the condition under which a job action should be triggered. 


### Translator

Translator: It converts the AI Graph into the Workflow that the scheduler can execute.

![Alt text](../images/architecture/translator.png)

The working steps of the translator are as follows:
1. A group of AI Nodes with the same job config are combined into an AISubGraph.
2. Call the corresponding JobGenerator according to the job config to convert all AISubGraphs to the corresponding Jobs.
3. Add all Control Edges to the Workflow.

## AIFlow Server
AIFlow Server provides meta information management and scheduling services.

### Meta Service

Meta Service: Provides the CRUD(Create, Read, Update and Delete) service of metadata generated in the workflow of machine learning tasks.

The services provided are shown in the figure below:

![Alt text](../images/architecture/meta.png)

1. Dataset: It provides dataset meta services, including data address, data format and other information.
   Users can define the program for reading and writing data according to it.
2. Project: It provides project meta services, 
   including project name, project description and other information.
   Users can organize the machine learning workflow of different projects based on it.
3. Workflow: It provides workflows meta services.
   Users can view the submitted workflow's meta according to it.
4. Model: It provides Models meta services.
   It contains the description information of the model and the version information of the model.
5. Metric: It provides metric meta services, such as model version evaluate metric.
6. Artifact: It provides artifacts meta services such as configuration files, jar packages etc.

### Scheduling Service

Scheduling Service: The Scheduling Service converts the workflow into an executable workflow 
and submits it to the scheduler.
The traditional scheduler could only support the scheduling of the batch jobs(It means that after upstream job finished, downstream jobs could run.) 
but in the online learning scenario where we have jobs that will never finish, it does not meet the demand. 
The scheduler for Scheduler Service docking must support event-based scheduling.

The following figure shows the principle of Scheduler Service:

![Alt text](../images/architecture/scheduling_service.png)

1. The user submits Workflow to the Scheduler Service.
2. The Scheduler Service forwards user requests to the scheduler based on event scheduling.
3. The scheduler manages the behavior of Workflow, such as running jobs, stopping jobs, etc.

## Notification Server

Notification Server: It provides Notification Service that supports the event publishing and subscription.
The functions of the Notification Server in the AIFlow system are as follows:
1. It provides sending/listening events for the scheduler. 
   For example, when a job ends, it will send an event representing the end of the job, 
   and the scheduler will perform the corresponding scheduling action after receiving this event.
   
2. It provides sending/listening events for the Meta Service.
   For example, a user registers a new model version.
   After receiving the user’s request, 
   the Meta Service will send an event representing the registration of a new model version.
   
3. It provides sending/listening events for the Jobs.
   For example, when a job to evaluate the model ends, 
   an event will be generated that represents the result of the model evaluation. 
   When the downstream job receives this event, it will perform the corresponding action.
   
4. It provides sending/listening events for the external system.
   The external system can send or listen to some user-defined events.


The figure below shows its working steps:

![Alt text](../images/architecture/notification.png)

1. A consumer listens the event which the key field equals 'Model'.
2. A producer sends the event to the Notification Server.
3. The consumer received the event, and then processes the received event according to the consumer's pre-defined logic.

## Scheduler

Scheduler: Scheduler is responsible for scheduling the workflow.

The figure below shows the difference between traditional scheduling and event-based scheduling:
![scheduler](../images/architecture/scheduler.png)
With the traditional scheduler, after upstream jobs finished, downstream jobs can run.
As shown above, after Job_1 and Job_2 are finished,Job_3 can run. 
After Job_3 and Job_4 are finished, Job_5 can run. 
After Job_3 is finished, Job_6 can run.

With the event-based scheduler, after receiving necessary events, downstream jobs can run.
As shown above, After receiving event_1 and event_2, Job_3 can run.
After receiving event_3 and event_4, Job_5 can run.
After receiving event_5, Job_6 can run.

At present, the default scheduler is an [event-based scheduler](https://github.com/flink-extended/ai-flow/tree/master/lib/airflow),
which is based on airflow.

## AIFlow Plugins

AIFlow provides a series of plugin interfaces for the connection with the external systems, 
which interfaces are as follows:

1. Scheduler plugin: It provides an interface to integrate with the scheduler. 
   Users can implement this interface to connect to different schedulers, such as AirFlow.
   
   Scheduler plugin interface definition: [Scheduler Interface](https://github.com/flink-extended/ai-flow/tree/master/ai_flow/plugin_interface/scheduler_interface.py)

2. Job plugin: It provides an interface for docking different types of jobs. 
   Users can implement this interface to dock different types of jobs, such as Bash job, Python job, etc.

   Job plugin interface definition: [Job Plugin Interface](https://github.com/flink-extended/ai-flow/tree/master/ai_flow/plugin_interface/job_plugin_interface.py)

3. BlobManager plugin: It provides an interface to store the project code in different media. 
   Users can implement this interface to store the project code in different storage media, such as oss, hdfs, etc.
   
   BlobManager plugin interface definition: [BlobManager Interface](https://github.com/flink-extended/ai-flow/tree/master/ai_flow/plugin_interface/blob_manager_interface.py)
