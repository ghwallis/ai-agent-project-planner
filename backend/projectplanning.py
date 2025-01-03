#!/usr/bin/env python
# coding: utf-8

# # L1: Automated Project: Planning, Estimation, and Allocation
# Warning control
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
from helper import load_env
load_env()

import os
import yaml
import pandas as pd
from crewai import Agent, Task, Crew
from tabulate import tabulate
from datetime import datetime

os.environ['OPENAI_MODEL_NAME'] = 'gpt-3.5-turbo'


# ## Loading Tasks and Agents YAML files

# Define file paths for YAML configurations
current_dir = os.path.dirname(os.path.abspath(__file__))
files = {
    'agents': os.path.join(current_dir, 'config', 'agents.yaml'),
    'tasks': os.path.join(current_dir, 'config', 'tasks.yaml')
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']


# ## Create Pydantic Models for Structured Output

from typing import List, Dict
from pydantic import BaseModel, Field

class TaskEstimate(BaseModel):
    task_name: str = Field(..., description="Name of the task")
    estimated_time_hours: float = Field(..., description="Estimated time to complete the task in hours")
    required_resources: List[str] = Field(..., description="List of resources required to complete the task")

class Milestone(BaseModel):
    milestone_name: str = Field(..., description="Name of the milestone")
    tasks: List[str] = Field(..., description="List of task IDs associated with this milestone")

class TeamMemberAssignment(BaseModel):
    task: str
    assignee: str
    start_date: str
    end_date: str

class ProjectPlan(BaseModel):
    project_requirements: str
    project_start_date: str
    project_end_date: str
    team_members: List[TeamMemberAssignment]


# ## Create Crew, Agents and Tasks
# Creating Agents
project_planning_agent = Agent(
  config=agents_config['project_planning_agent']
)

estimation_agent = Agent(
  config=agents_config['estimation_agent']
)

resource_allocation_agent = Agent(
  config=agents_config['resource_allocation_agent']
)

# Creating Tasks
task_breakdown = Task(
  config=tasks_config['task_breakdown'],
  agent=project_planning_agent
)

time_resource_estimation = Task(
  config=tasks_config['time_resource_estimation'],
  agent=estimation_agent
)

resource_allocation = Task(
  config=tasks_config['resource_allocation'],
  agent=resource_allocation_agent,
  output_pydantic=ProjectPlan # This is the structured output we want
)

# Creating Crew
crew = Crew(
  agents=[
    project_planning_agent,
    estimation_agent,
    resource_allocation_agent
  ],
  tasks=[
    task_breakdown,
    time_resource_estimation,
    resource_allocation
  ],
  verbose=True
)


# ## Crew's Inputs

from IPython.display import display, Markdown

project = ''
industry = ''
project_objectives = ''
team_members = ''
project_requirements = ''
project_start_date = 'yyyy-mm-dd'
project_end_date = 'yyyy-mm-dd'

# Format the dictionary as Markdown for a better display in Jupyter Lab
formatted_output = f"""
**Project Type:** {project}

**Project Objectives:** {project_objectives}

**Industry:** {industry}

**Team Members:**
{team_members}
**Project Requirements:**
{project_requirements}

**Project Start Date:** {project_start_date}
**Project End Date:** {project_end_date}
"""
# Display the formatted output as Markdown
display(Markdown(formatted_output))


# ## Kicking off the crew

def create_gantt_chart(tasks_df, milestones_df, start_date, end_date):
    import plotly.figure_factory as ff
    from datetime import timedelta
    
    # Convert string dates to datetime if they aren't already
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Calculate total project duration
    total_duration = (end_date - start_date).days
    
    # Calculate time per task based on estimated hours
    total_hours = tasks_df['estimated_time_hours'].sum()
    hours_to_days_ratio = total_duration / (total_hours or 1)
    
    # Prepare data for Gantt chart
    gantt_data = []
    current_date = start_date

    # Add tasks
    for _, task in tasks_df.iterrows():
        if task['estimated_time_hours'] == 0:
            continue
            
        task_days = max(1, int(task['estimated_time_hours'] * hours_to_days_ratio))
        duration = timedelta(days=task_days)
        
        gantt_data.append(dict(
            Task=task['task_name'],
            Start=current_date,
            Finish=current_date + duration,
            Resource=task['required_resources']
        ))
        current_date = current_date + duration + timedelta(days=1)  # Add a day gap between tasks

    # Create a DataFrame for the Gantt data
    gantt_df = pd.DataFrame(gantt_data)
    
    # Convert dates to strings in ISO format for JSON serialization
    gantt_df['Start'] = gantt_df['Start'].dt.strftime('%Y-%m-%d')
    gantt_df['Finish'] = gantt_df['Finish'].dt.strftime('%Y-%m-%d')
    
    return gantt_df

def export_to_excel(tasks_df, milestones_df, gantt_df, filename='project_plan.xlsx'):
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        # Write Tasks sheet
        tasks_df.to_excel(writer, sheet_name='Tasks', index=False)
        
        # Write Milestones sheet
        milestones_df.to_excel(writer, sheet_name='Milestones', index=False)
        
        # Write Gantt Data sheet
        if gantt_df is not None:
            gantt_df.to_excel(writer, sheet_name='Gantt Timeline', index=False)
            
        # Get the workbook and add some formatting
        workbook = writer.book
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1
        })
        
        # Format each worksheet
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            # Get the dataframe for this sheet
            if sheet_name == 'Tasks':
                df = tasks_df
            elif sheet_name == 'Milestones':
                df = milestones_df
            elif sheet_name == 'Gantt Timeline' and gantt_df is not None:
                df = gantt_df
            
            # Write headers with formatting
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                # Auto-adjust column width based on content
                max_length = max(
                    df[value].astype(str).apply(len).max(),
                    len(str(value))
                ) + 2
                worksheet.set_column(col_num, col_num, max_length)

def categorize_tasks_into_milestones(tasks, project_type):
    # Create a milestone categorization agent
    milestone_agent = Agent(
        role="Milestone Categorization Expert",
        goal="Categorize project tasks into appropriate milestones",
        backstory="Expert in project management and milestone planning with deep understanding of project phases",
        verbose=True,
        allow_delegation=False,
        tools=[]
    )
    
    # Prepare the task description
    task_list = "\n".join([f"- {task['task_name']}" for task in tasks])
    
    # Create a Task for the milestone categorization
    categorization_task = Task(
        description=f"""
        For the {project_type} project, categorize these tasks into appropriate milestones:

        {task_list}

        Consider the following milestone categories:
        1. Initial Setup (foundation and basic infrastructure)
        2. Core Development (main functionality and features)
        3. Final Implementation (completion, integration, and deployment)

        Ensure every task is assigned to exactly one milestone based on its logical phase in the project.
        """,
        expected_output="""A JSON object with milestone categorizations in this format:
        {
            "milestones": [
                {
                    "milestone_name": "string",
                    "tasks": ["task_name1", "task_name2", ...]
                }
            ]
        }""",
        agent=milestone_agent
    )

    # Create a crew for milestone categorization
    milestone_crew = Crew(
        agents=[milestone_agent],
        tasks=[categorization_task],
        verbose=True
    )

    try:
        # Execute the crew
        result = milestone_crew.kickoff()
        
        # Parse the JSON response
        import json
        # Find JSON in the response
        response_str = str(result)
        json_start = response_str.find('{')
        json_end = response_str.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_str[json_start:json_end]
            categorized = json.loads(json_str)
            return categorized['milestones']
        else:
            raise ValueError("No valid JSON found in response")
            
    except Exception as e:
        print(f"Error parsing milestone categorization: {e}")
        # Fallback to default categorization
        return [
            {
                'milestone_name': 'Initial Setup',
                'tasks': [t['task_name'] for t in tasks[:3]]
            },
            {
                'milestone_name': 'Core Development',
                'tasks': [t['task_name'] for t in tasks[3:7]]
            },
            {
                'milestone_name': 'Final Implementation',
                'tasks': [t['task_name'] for t in tasks[7:]]
            }
        ]

def create_project_plan(data):
    try:
        # Create the agents
        project_planning_agent = Agent(
            role="Project Planning Expert",
            goal="Create detailed project plans with tasks, timelines, and resource allocations",
            backstory="Experienced in breaking down complex projects into manageable tasks",
            verbose=True
        )

        estimation_agent = Agent(
            role="Project Estimation Specialist",
            goal="Provide accurate time and resource estimates for project tasks",
            backstory="Specialized in project estimation with years of experience",
            verbose=True
        )

        resource_allocation_agent = Agent(
            role="Resource Management Expert",
            goal="Optimize resource allocation across project tasks",
            backstory="Expert in managing and allocating project resources efficiently",
            verbose=True
        )

        # Prepare the inputs
        formatted_requirements = '\n'.join([f"- {req}" for req in data.get('project_requirements', [])])
        formatted_team = '\n'.join([f"- {member}" for member in data.get('team_members', [])])

        # Create tasks
        task_breakdown = Task(
            description=f"""
            Analyze the project requirements and break them down into individual tasks:
            
            Project: {data.get('project_name')}
            Industry: {data.get('industry')}
            Requirements:
            {formatted_requirements}
            
            Team Members:
            {formatted_team}
            """,
            expected_output="""A JSON object with this structure:
            {
                "tasks": [
                    {
                        "task": "task description",
                        "assignee": "team member name"
                    }
                ]
            }""",
            agent=project_planning_agent
        )

        # Create crew
        crew = Crew(
            agents=[project_planning_agent, estimation_agent, resource_allocation_agent],
            tasks=[task_breakdown],
            verbose=True
        )

        # Run the crew
        result = crew.kickoff()

        # Process the results - try to parse JSON from the result
        try:
            import json
            # Find JSON in the response
            response_str = str(result)
            json_start = response_str.find('{')
            json_end = response_str.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_str[json_start:json_end]
                result_data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")

            # Process tasks
            tasks = []
            for task_info in result_data.get('tasks', []):
                try:
                    assignees = task_info.get('assignee', '').split(',')
                    assignees = [a.strip().split(' (')[0] for a in assignees]

                    tasks.append({
                        'task_name': task_info.get('task', ''),
                        'required_resources': assignees,
                        'estimated_time_hours': 40  # Default to 1 week
                    })
                except Exception as e:
                    print(f"Warning: Could not process task: {str(e)}")
                    continue

            if not tasks:
                raise ValueError("No tasks were generated")

            # Categorize tasks into milestones
            milestones = categorize_tasks_into_milestones(tasks, data.get('project_name', 'Project'))

            # Create DataFrames
            tasks_df = pd.DataFrame(tasks)
            milestones_df = pd.DataFrame(milestones)

            # Format the data
            tasks_df = tasks_df.round(2)
            if not tasks_df.empty:
                tasks_df['required_resources'] = tasks_df['required_resources'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

            # Create Gantt chart
            gantt_df = create_gantt_chart(tasks_df, milestones_df, data['project_start_date'], data['project_end_date'])

            # Export to Excel
            export_to_excel(tasks_df, milestones_df, gantt_df)

            # Before returning, log the Gantt data
            gantt_data = gantt_df.to_dict('records')
            print("Returning Gantt data:", gantt_data)
            
            return {
                'success': True,
                'tasks': [{
                    'Task Name': task['task_name'],
                    'Estimated Hours': task['estimated_time_hours'],
                    'Assigned To': task['required_resources']
                } for task in tasks_df.to_dict('records')],
                'milestones': [{
                    'Milestone': m['milestone_name'],
                    'Tasks': m['tasks']
                } for m in milestones_df.to_dict('records')],
                'gantt_chart': gantt_data
            }

        except Exception as e:
            print(f"Error processing crew result: {str(e)}")
            raise ValueError(f"Failed to process crew output: {str(e)}")

    except Exception as e:
        print(f"Error in create_project_plan: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }







