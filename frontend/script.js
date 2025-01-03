document.getElementById('projectForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // Show loading spinner
    document.getElementById('loadingSpinner').classList.remove('d-none');
    
    // Get form data
    const formData = {
        project_name: document.getElementById('projectName').value,
        industry: document.getElementById('industry').value,
        project_objectives: document.getElementById('projectObjectives').value,
        team_members: document.getElementById('teamMembers').value.split('\n'),
        project_requirements: document.getElementById('projectRequirements').value.split('\n'),
        project_start_date: document.getElementById('projectStartDate').value,
        project_end_date: document.getElementById('projectEndDate').value
    };

    try {
        const response = await fetch('http://localhost:5000/generate-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            // Display tasks table
            document.getElementById('tasksTable').innerHTML = createTable(data.tasks, 'Tasks Breakdown');
            
            // Display milestones table
            document.getElementById('milestonesTable').innerHTML = createTable(data.milestones, 'Milestones');
            
            // Create Gantt chart
            createGanttChart(data.gantt_chart);
        } else {
            alert('Error generating project plan: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating project plan. Please try again.');
    } finally {
        // Hide loading spinner
        document.getElementById('loadingSpinner').classList.add('d-none');
    }
});

function createTable(data, title) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    
    return `
        <div class="table-container">
            <h3>${title}</h3>
            <table class="table table-striped">
                <thead>
                    <tr>
                        ${headers.map(h => `<th>${formatHeader(h)}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${data.map(row => `
                        <tr>
                            ${headers.map(h => `<td>${formatCell(row[h])}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function formatHeader(header) {
    return header.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function formatCell(content) {
    if (Array.isArray(content)) {
        // Format array of tasks as bullet points
        return `<ul class="mb-0">
            ${content.map(task => `<li>${task}</li>`).join('')}
        </ul>`;
    }
    if (typeof content === 'string' && content.includes('\n')) {
        return content.split('\n').join('<br>');
    }
    return content;
}

function createGanttChart(data) {
    if (!data || data.length === 0) {
        console.log("No data available for Gantt chart");
        document.getElementById('ganttChart').innerHTML = '<p class="text-muted">No timeline data available</p>';
        return;
    }

    console.log("Gantt chart data:", data);

    const tasks = data.map(task => ({
        Task: task.Task,
        Start: new Date(task.Start),
        Finish: new Date(task.Finish),
        Resource: task.Resource
    }));

    // Create color mapping
    const uniqueResources = [...new Set(tasks.map(t => t.Resource))];
    const colors = {};
    uniqueResources.forEach((resource, i) => {
        colors[resource] = `rgb(${i * 30 % 255}, ${(i * 60) % 255}, ${(i * 90) % 255})`;
    });

    // Create Gantt chart data
    const ganttData = [{
        type: 'bar',
        x: tasks.map(t => {
            const duration = (t.Finish - t.Start) / (1000 * 60 * 60 * 24); // Duration in days
            return duration;
        }),
        y: tasks.map(t => t.Task),
        orientation: 'h',
        marker: {
            color: tasks.map(t => colors[t.Resource])
        },
        text: tasks.map(t => `${t.Resource}<br>${t.Start.toLocaleDateString()} - ${t.Finish.toLocaleDateString()}`),
        hoverinfo: 'text',
        name: 'Tasks'
    }];

    const layout = {
        title: 'Project Timeline',
        height: Math.max(400, tasks.length * 40),
        xaxis: {
            title: 'Duration (Days)',
            showgrid: true
        },
        yaxis: {
            title: 'Tasks',
            showgrid: true
        },
        margin: {
            l: 200,
            r: 20,
            t: 50,
            b: 100
        }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    try {
        Plotly.newPlot('ganttChart', ganttData, layout, config);
    } catch (error) {
        console.error("Error creating Gantt chart:", error);
        document.getElementById('ganttChart').innerHTML = 
            `<div class="alert alert-warning">Error creating timeline: ${error.message}</div>`;
    }
}
