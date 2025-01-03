# AI Project Planning Assistant

An intelligent project planning tool that uses AI agents from CrewAI to break down project requirements, estimate timelines, and allocate resources. The system generates detailed task breakdowns, milestone categorizations, and interactive Gantt charts.

## Features

- 🤖 **AI-powered project planning** using multiple specialized agents
- 📊 **Interactive Gantt chart visualization**
- 📋 **Automatic task breakdown and estimation**
- 🎯 **Smart milestone categorization**
- 📅 **Resource allocation and timeline management**
- 📑 **Excel export functionality**

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap, Plotly.js
- **Backend**: Python, Flask, CrewAI
- **AI**: OpenAI GPT Models
- **Data Handling**: Pandas, YAML

## Installation

### 1. Clone the repository:
```bash
git clone https://github.com/ghwallis/ai-project-planning.git
cd ai-project-planning
```

### 2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables:
Create a `.env` file in the root directory with:
```env
OPENAI_API_KEY=your_api_key_here
```

## Project Structure
```
├── backend/
│   ├── config/
│   │   ├── agents.yaml
│   │   └── tasks.yaml
│   ├── app.py
│   ├── helper.py
│   └── projectplanning.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Usage

### 1. Start the backend server:
```bash
cd backend
python app.py
```

### 2. Open the frontend in your browser:
Open `frontend/index.html` in your web browser or serve it using a local server.

### 3. Fill in the project details:
   - Project name and industry
   - Project objectives
   - Team members (one per line)
   - Project requirements
   - Start and end dates

### 4. Generate your project plan:
Click **"Generate Plan"** to create your project plan.

## Features in Detail

### AI Agents

- **Project Planning Expert**: Breaks down requirements into tasks.
- **Estimation Specialist**: Provides time and resource estimates.
- **Resource Management Expert**: Optimizes resource allocation.

### Output

- Detailed task breakdown with estimates.
- Milestone categorization.
- Interactive Gantt chart.
- Resource allocation plan.
- Exportable Excel report.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- CrewAI for the AI agent framework.
- OpenAI for the language models.
- Plotly.js for visualization.
