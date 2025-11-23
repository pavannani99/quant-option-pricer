"""Common UI components for all pages"""
import streamlit as st


def render_header(page_title: str):
    """Render common header with theme toggle and LinkedIn"""
    # Theme toggle at the top
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        st.title(page_title)
    with col3:
        theme_label = "☀️ Light" if st.session_state.get('theme', 'light') == 'dark' else "🌙 Dark"
        if st.button(theme_label, key=f"theme_toggle_{page_title}"):
            st.session_state.theme = 'dark' if st.session_state.get('theme', 'light') == 'light' else 'light'
            st.rerun()


def render_footer():
    """Render footer with LinkedIn"""
    st.markdown("---")
    linkedin_url = "https://www.linkedin.com/in/pavan-nani/"
    st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <p style="margin: 5px;">Created by <strong>Simhadri Pavan Kumar</strong></p>
            <a href="{linkedin_url}" target="_blank" style="text-decoration: none;">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="30" height="30" style="vertical-align: middle;">
                <span style="margin-left: 10px; color: #0077b5; font-weight: bold;">Connect on LinkedIn</span>
            </a>
        </div>
    """, unsafe_allow_html=True)


def init_theme():
    """Initialize theme in session state"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
