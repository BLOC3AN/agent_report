import streamlit as st
import os
from dotenv import load_dotenv
from src.agents.agent_report import AgentReporter

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Agent Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        margin-top: 1rem;
    }
    .report-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Agent Report Service")
st.sidebar.image("https://img.icons8.com/color/96/000000/google-sheets.png", width=100)
st.sidebar.markdown("---")
st.sidebar.markdown("Generate daily reports from Google Sheets using AI.")

# Main content
st.title("📊 Agent Report Generator")

# URL input
default_url = os.getenv("url", "")
url = st.text_input("Google Sheet URL", value=default_url)

# Generate report button
if st.button("Generate Report", type="primary"):
    if url:
        with st.spinner("Generating report... This may take a few seconds."):
            try:
                # Initialize agent and run
                agent = AgentReporter(url)
                report = agent.run()
                
                # Display report
                st.markdown("## Generated Report")
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(report)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Download button
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name="agent_report.md",
                    mime="text/markdown"
                )
                
                # Display conversation history
                with st.expander("View Conversation History"):
                    messages = agent.get_conversation_history()
                    for i, msg in enumerate(messages):
                        if hasattr(msg, 'type') and msg.type == 'system':
                            continue
                        
                        if hasattr(msg, 'type') and msg.type == 'human':
                            st.markdown(f"**User:** {msg.content}")
                        elif hasattr(msg, 'type') and msg.type == 'ai':
                            st.markdown(f"**AI:** {msg.content}")
                        elif hasattr(msg, 'type') and msg.type == 'tool':
                            st.markdown(f"**Tool:** {msg.name}")
                            st.code(msg.content)
            
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    else:
        st.warning("Please enter a Google Sheet URL")

# Help section
with st.expander("How to use"):
    st.markdown("""
    1. Enter the URL of your Google Sheet containing report data
    2. Click "Generate Report" to create a formatted report
    3. View and download the generated report
    
    **Note:** The Google Sheet should have the following columns:
    - Date
    - Inprogress
    - Blocker
    - Completed
    
    The service will automatically extract the most recent data entry.
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Agent Report Service v1.0")