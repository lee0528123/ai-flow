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
import inspect
import os
import sys
import tempfile
import traceback
from typing import Text
from ai_flow.context.project_context import init_project_context, current_project_config, set_current_project_config
from ai_flow.context.workflow_config_loader import init_workflow_config
from ai_flow.client.ai_flow_client import get_ai_flow_client

__init_context_flag__ = False
__init_client_flag__ = False

from ai_flow.project.project_config import ProjectConfig
from ai_flow.workflow.workflow_config import WorkflowConfig, dump_workflow_config


def init_ai_flow_context():
    """
    When defining the ai flow program,
    you need to call this function to initialize the project and workflow environment information.
    This function has three functions:
    1. Init project context
    2. Init project configuration
    3. Init workflow configuration.
    """
    global __init_context_flag__
    if __init_context_flag__:
        raise Exception('init_ai_flow_context and init_notebook_context cannot be called at the same time.')
    if __init_client_flag__:
        raise Exception('init_ai_flow_client and init_ai_flow_context cannot be called at the same time.')
    stack = traceback.extract_stack()
    workflow_entry_file = os.path.abspath(stack[-2].filename)
    workflows_path = os.path.dirname(os.path.dirname(workflow_entry_file))
    # workflow_name/workflow_name.py len(.py) == 3
    workflow_name = os.path.basename(workflow_entry_file)[:-3]
    project_path = os.path.dirname(workflows_path)
    init_project_context(project_path)
    ensure_project_registered()
    # workflow_name/workflow_name.yaml
    init_workflow_config(workflow_config_file
                         =os.path.join(workflows_path, workflow_name, '{}.yaml'.format(workflow_name)))
    __init_context_flag__ = True


def init_notebook_context(project_config: ProjectConfig, workflow_config: WorkflowConfig):
    """
    Initializes the notebook context for the project and workflow environment when user defines the workflow:
    1. Generates project and workflow.
    2. Initializes project context.
    3. Initializes project configuration.
    4. Initializes workflow configuration.
    """
    global __init_context_flag__
    if __init_context_flag__:
        raise Exception('init_notebook_context and init_ai_flow_context cannot be called at the same time.')

    def generate(workflow_code):
        """
        Generates the project and workflow automatically.

        :param workflow_code: User-defined workflow code.
        :return: Project path and workflow configuration path.
        """
        temp_path = tempfile.mkdtemp()
        temp_project_path = '{}/{}'.format(temp_path, project_config.get_project_name())
        workflow_name = workflow_config.workflow_name
        temp_workflow_path = '{}/workflows/{}'.format(temp_project_path, workflow_name)
        os.makedirs(temp_workflow_path)
        project_config.dump_to_file('{}/project.yaml'.format(temp_project_path))
        temp_workflow_config = '{}/{}.yaml'.format(temp_workflow_path, workflow_name)
        dump_workflow_config(workflow_config, temp_workflow_config)
        with open('{}/{}.py'.format(temp_workflow_path, workflow_name), 'w') as f:
            f.write(workflow_code)
        return temp_project_path, temp_workflow_config

    project_path, workflow_config_path = generate(inspect.getsource(sys._getframe().f_back.f_back))
    init_project_context(project_path)
    ensure_project_registered()
    init_workflow_config(workflow_config_path)
    __init_context_flag__ = True


def ensure_project_registered():
    """ Ensure the project configured in project.yaml has been registered. """

    client = get_ai_flow_client()
    project_meta = client.get_project_by_name(current_project_config().get_project_name())
    pp = {}
    for k, v in current_project_config().items():
        pp[k] = str(v)
    if project_meta is None:
        project_meta = client.register_project(name=current_project_config().get_project_name(),
                                               properties=pp)
    else:
        project_meta = client.update_project(project_name=current_project_config().get_project_name(), properties=pp)

    current_project_config().set_project_uuid(str(project_meta.uuid))


def init_ai_flow_client(server_uri: Text, project_name: Text = None, **kwargs):
    """ Initializes the :class:`ai_flow.client.ai_flow_client.AIFlowClient`.
        It's suitable for using AIFlowClient separately in per job.
    """
    if __init_context_flag__ is True:
        raise Exception('init_ai_flow_client and init_ai_flow_context cannot be called at the same time.')
    config_dict = {'server_uri': server_uri}
    if project_name is None:
        project_name = 'Unknown'
    config_dict['project_name'] = project_name
    for k, v in kwargs.items():
        config_dict[k] = v
    set_current_project_config(config_dict)
    ensure_project_registered()
    global __init_client_flag__
    __init_client_flag__ = True
