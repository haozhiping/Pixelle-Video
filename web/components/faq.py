# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
FAQ component for displaying frequently asked questions
"""

from pathlib import Path
from typing import Optional

import streamlit as st
from loguru import logger

from web.i18n import get_language, tr


def load_faq_content(language: str) -> Optional[str]:
    """
    Load FAQ content based on current language
    
    Args:
        language: Current language code (e.g., "zh_CN", "en_US")
    
    Returns:
        FAQ content as markdown string, or None if file not found
    """
    # Determine which FAQ file to load based on language
    # For Chinese (zh_CN), use FAQ_CN.md
    # For all other languages, use FAQ.md (English)
    project_root = Path(__file__).resolve().parent.parent.parent
    
    if language.startswith("zh"):
        faq_file = project_root / "docs" / "FAQ_CN.md"
    else:
        faq_file = project_root / "docs" / "FAQ.md"
    
    try:
        if faq_file.exists():
            with open(faq_file, "r", encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"Loaded FAQ from: {faq_file}")
            return content
        else:
            logger.warning(f"FAQ file not found: {faq_file}")
            return None
    except Exception as e:
        logger.error(f"Failed to load FAQ file {faq_file}: {e}")
        return None


def render_faq_sidebar():
    """
    Render FAQ in the sidebar
    
    This component displays frequently asked questions in the sidebar,
    allowing users to quickly find answers without leaving the main interface.
    """
    with st.sidebar:
        # FAQ header with icon
        # st.markdown(f"### 🙋‍♀️ {tr('faq.title', fallback='FAQ')}")
        
        # Get current language
        current_language = get_language()
        
        # Load FAQ content
        faq_content = load_faq_content(current_language)
        
        if faq_content:
            # Display FAQ in an expander, expanded by default
            with st.expander(tr('faq.expand_to_view', fallback='FAQ'), expanded=True):
                # Remove the first heading from FAQ content since we already show it above
                lines = faq_content.split('\n')
                # Skip the first line if it's a heading
                if lines and lines[0].startswith('#'):
                    faq_content = '\n'.join(lines[1:])
                
                # Display FAQ content
                st.markdown(faq_content, unsafe_allow_html=True)
            
            # Add a link to MySoAI Video for more help
            st.markdown(
                f"💡 {tr('faq.more_help', fallback='Need more help?')} "
                f"[MySoAI Video](https://ai.feishu.cn/wiki/PAaYwlVrpishg5kQXQocxYG0n4f)"
            )
        else:
            # If FAQ cannot be loaded, only show the GitHub link
            st.markdown(f"### 💡 {tr('faq.more_help', fallback='Need help?')}")
            st.markdown(
                f"[MySoAI Video](https://ai.feishu.cn/wiki/PAaYwlVrpishg5kQXQocxYG0n4f) | "
                f"[Documentation](https://aidc-ai.github.io/Pixelle-Video)"
            )
