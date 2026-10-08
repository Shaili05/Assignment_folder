import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import base64
from html import escape as html_escape
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone

import altair as alt
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

from src.frontend import api_client, chat_store, suggestions
from src.config.constants import (
    AVAILABLE_MODELS, DEFAULT_MODEL, LOW_SAMPLE_THRESHOLD, MAX_TREND_PERIODS, PROFILE_SENSITIVE_COLUMNS,
    PROGRESS_POLL_SEC, ROLE_LABELS, SENTIMENTS, SEVERITY_LEVELS, STAGE_LABELS, STAGE_TOOL_START, TOOL_LABELS,
)


st.set_page_config(page_title="Review Intelligence", layout="wide")


BRAND_SECTIONS = ["Overview", "Trends", "Flagged reviews", "Assistant", "Audit log"]
SUPPORT_SECTIONS = ["Flagged reviews", "Assistant", "Audit log"]

SENTIMENT_COLORS = {"positive": "#2fa860", "neutral": "#8a8f98", "negative": "#d6423c"}
SEVERITY_COLORS = {"low": "#3d8bfd", "medium": "#f0952e", "high": "#d6423c"}
SEVERITY_LABELS = {
    "low": "Low (score under 0.5)",
    "medium": "Medium (0.5 to 0.74)",
    "high": "High (0.75 and above)",
}
ASPECT_LABELS = {
    "packaging": "Packaging",
    "price": "Price",
    "texture_effectiveness": "Texture and results",
    "availability": "Availability",
}
ACCENT = "#1565c0"
TREND_LINE_COLOR = "#8fb8e8"
TREND_POINT_COLOR = "#f4a6b8"
PASTEL_BAR_COLORS = ["#9ec9e8", "#f6c28b", "#a9dcb5", "#e7b2e0", "#b3a8ee", "#f2a6a6", "#8fd6d0"]
HISTORY_LABEL_CHARS = 28
PANEL_HEIGHT = 430


def _svg_avatar(bg, inner_svg):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">'
        f'<circle cx="20" cy="20" r="20" fill="{bg}"/>{inner_svg}</svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


ASSISTANT_AVATAR = _svg_avatar(
    ACCENT,
    '<rect x="11" y="13" width="18" height="14" rx="4" fill="white"/>'
    '<circle cx="16" cy="20" r="2" fill="' + ACCENT + '"/>'
    '<circle cx="24" cy="20" r="2" fill="' + ACCENT + '"/>'
    '<rect x="18" y="7" width="4" height="6" rx="2" fill="white"/>',
)
USER_AVATAR = _svg_avatar(
    "#455a64",
    '<path d="M11 29c1.5-5 6-7 9-7s7.5 2 9 7" stroke="white" stroke-width="2.4" '
    'fill="none" stroke-linecap="round"/>'
    '<circle cx="20" cy="15" r="5.5" fill="white"/>',
)


PAGE_STYLE = f"""
<style>
[data-testid="stElementToolbar"] {{display: none;}}
[data-testid="stAppDeployButton"] {{display: none;}}
footer {{visibility: hidden;}}
.section-caption {{
    font-size: 0.92rem;
    line-height: 1.5;
    margin-bottom: 0.75rem;
}}
h1, h2, h3, h4 {{
    letter-spacing: 0.01em;
}}
[data-testid="stMarkdownContainer"] p {{
    line-height: 1.55;
}}
.html-table {{
    overflow: auto;
    border: 1px solid rgba(150, 150, 150, 0.25);
    border-radius: 8px;
}}
.html-table table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.87rem;
}}
.html-table th {{
    position: sticky;
    top: 0;
    background: #10151c;
    color: #eef3f8;
    text-align: left;
    padding: 8px 10px;
    border-bottom: 1px solid rgba(150, 150, 150, 0.3);
    white-space: nowrap;
}}
.html-table td {{
    padding: 7px 10px;
    border-bottom: 1px solid rgba(150, 150, 150, 0.12);
    vertical-align: top;
    max-width: 480px;
    white-space: normal;
    word-break: break-word;
}}
.html-table tr:hover td {{
    background: rgba(128, 128, 128, 0.12);
}}
.severity-badge {{ font-weight: 700; }}
.live-status {{
    display: flex;
    align-items: center;
    gap: 0.55rem;
    color: #6b7280;
    font-size: 0.9rem;
    padding: 0.2rem 0;
}}
.live-status .dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: {ACCENT};
    animation: live-pulse 1.1s ease-in-out infinite;
}}
@keyframes live-pulse {{
    0%, 100% {{ opacity: 0.25; transform: scale(0.8); }}
    50% {{ opacity: 1; transform: scale(1); }}
}}
[data-testid="stHorizontalBlock"] button {{
    font-size: 1.05rem;
    min-height: 2.3rem;
}}
[class*="st-key-open_"] button {{
    justify-content: flex-start;
    text-align: left;
}}
[class*="st-key-open_"] button p {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.block-container, [data-testid="stMainBlockContainer"] {{
    padding-top: 2.5rem;
}}
.flag-table {{
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.87rem;
}}
.flag-table th {{
    background: #10151c;
    color: #eef3f8;
    text-align: left;
    padding: 8px 10px;
    border-bottom: 1px solid rgba(150, 150, 150, 0.3);
    white-space: nowrap;
}}
.flag-table td {{
    padding: 7px 10px;
    border-bottom: 1px solid rgba(150, 150, 150, 0.12);
    vertical-align: top;
    word-break: break-word;
}}
.flag-table td.nowrap {{ white-space: nowrap; }}
.flag-table tr:hover td {{ background: rgba(128, 128, 128, 0.12); }}
.flag-table summary {{
    display: block;
    cursor: pointer;
    list-style: none;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.flag-table summary::-webkit-details-marker {{ display: none; }}
.flag-table details[open] summary {{
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
}}
.flag-table th.edge .flag-tip {{ left: auto; right: 0; }}
[data-testid="stTooltipIcon"] svg {{ display: none; }}
[data-testid="stTooltipIcon"]::after {{
    content: "\\24D8";
    font-size: 1.05rem;
    line-height: 1;
}}
[data-testid="stDialog"] div[role="dialog"] {{ width: min(1250px, 96vw); }}
.profile-head {{
    display: flex;
    flex-wrap: wrap;
    gap: 1rem 2.5rem;
    padding: 0.9rem 1.1rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(150, 150, 150, 0.3);
    border-radius: 8px;
}}
.profile-item .label {{
    font-size: 0.72rem;
    opacity: 0.7;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.profile-item .value {{ font-weight: 600; }}
.profile-scroll {{
    max-height: 50vh;
    overflow: auto;
    border: 1px solid rgba(150, 150, 150, 0.3);
    border-radius: 8px;
}}
.profile-table {{
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.82rem;
}}
.profile-table th {{
    position: sticky;
    top: 0;
    z-index: 1;
    background: #10151c;
    color: #eef3f8;
    text-align: left;
    padding: 8px 10px;
}}
.profile-table td {{
    padding: 7px 10px;
    border-bottom: 1px solid rgba(150, 150, 150, 0.15);
    vertical-align: top;
    word-break: break-word;
}}
.profile-table .name {{ font-weight: 600; }}
.profile-table .desc {{ font-size: 0.74rem; opacity: 0.7; margin-top: 2px; }}
.profile-table .muted {{ opacity: 0.6; font-style: italic; }}
</style>
"""


def new_session_id():
    return uuid.uuid4().hex[:10]


def init_state():
    defaults = {
        "session_id": new_session_id(),
        "messages": [],
        "section": None,
        "queued_question": None,
        "pending_question": None,
        "history_collapsed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def persist_conversation(role):
    if st.session_state.messages:
        chat_store.save_conversation(st.session_state.session_id, role, st.session_state.messages)


def start_new_conversation(role):
    persist_conversation(role)
    st.session_state.session_id = new_session_id()
    st.session_state.messages = []


def open_conversation(session_id, role):
    persist_conversation(role)
    st.session_state.session_id = session_id
    st.session_state.messages = chat_store.load_conversation(session_id)


def agent_status_box(model):
    try:
        status = api_client.get_assistant_status(model)
    except requests.RequestException as exc:
        st.error(f"Cannot reach the backend API: {exc}")
        return
    if status["error"]:
        st.error(f"Assistant is offline: {status['error']}")
    elif status["ready"]:
        st.success("Assistant is ready to answer your questions.")
    elif status["started"]:
        st.info("Assistant is warming up, this takes up to a minute.")
    else:
        st.info("Assistant has not started yet. Ask a question to start it.")


def render_sidebar():
    st.sidebar.title("Review Intelligence")
    if "role" not in st.query_params:
        st.query_params["role"] = "brand_manager"
    role = st.query_params.get("role", "brand_manager")
    if role not in ROLE_LABELS:
        st.query_params["role"] = "brand_manager"
        role = "brand_manager"
    st.sidebar.caption(f"Role: {ROLE_LABELS[role]}")

    model = st.sidebar.selectbox(
        "Model", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index(DEFAULT_MODEL) if DEFAULT_MODEL in AVAILABLE_MODELS else 0,
        help="Changing the model starts a new assistant session on the backend.",
    )

    def status():
        agent_status_box(model)

    with st.sidebar:
        st.fragment(run_every=20)(status)()

    return role, model


def render_nav(sections):
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)
    current = st.session_state.section if st.session_state.section in sections else sections[0]
    selected = st.radio(
        "section-nav", sections, index=sections.index(current), horizontal=True,
        label_visibility="collapsed", key="section_nav",
    )
    st.session_state.section = selected
    st.divider()
    return selected


def caption(text):
    st.markdown(f"<div class='section-caption'>{text}</div>", unsafe_allow_html=True)


def draw(chart):
    styled = (
        chart
        .configure_axis(labelLimit=500, labelFontSize=12)
        .configure_legend(labelLimit=500)
    )
    try:
        st.altair_chart(styled, width="stretch")
    except TypeError:
        st.altair_chart(styled, use_container_width=True)


def render_html_table(styler, max_height=420):
    try:
        styler = styler.hide(axis="index")
    except AttributeError:
        styler = styler.hide_index()
    html = styler.format(escape="html").to_html()
    st.markdown(f"<div class='html-table' style='max-height:{max_height}px;'>{html}</div>",
                unsafe_allow_html=True)


def aspect_chart(aspects):
    rows = []
    for item in aspects:
        label = f"{ASPECT_LABELS.get(item['aspect'], item['aspect'])} ({item['n_reviews']:,})"
        for sentiment in SENTIMENTS:
            rows.append({"aspect": label, "sentiment": sentiment, "share": item["pct"][sentiment]})
    data = pd.DataFrame(rows)
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            y=alt.Y("aspect:N", title=None, sort=None),
            x=alt.X("share:Q", title="Share of reviews (%)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color(
                "sentiment:N", title=None, sort=SENTIMENTS,
                scale=alt.Scale(domain=list(SENTIMENT_COLORS), range=list(SENTIMENT_COLORS.values())),
                legend=alt.Legend(orient="bottom"),
            ),
            order=alt.Order("sentiment:N", sort="descending"),
            tooltip=[alt.Tooltip("aspect:N", title="Aspect"), alt.Tooltip("sentiment:N", title="Sentiment"),
                     alt.Tooltip("share:Q", title="Share (%)", format=".1f")],
        )
        .properties(height=230)
    )
    draw(chart)


def severity_chart(severity_counts, issue_type_counts):
    data = pd.DataFrame({
        "level": SEVERITY_LEVELS,
        "severity": [SEVERITY_LABELS[level] for level in SEVERITY_LEVELS],
        "reviews": [severity_counts.get(level, 0) for level in SEVERITY_LEVELS],
    })
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            y=alt.Y("severity:N", title=None, sort=None),
            x=alt.X("reviews:Q", title="Flagged reviews"),
            color=alt.Color("level:N", legend=None,
                            scale=alt.Scale(domain=SEVERITY_LEVELS, range=[SEVERITY_COLORS[s] for s in SEVERITY_LEVELS])),
            tooltip=[alt.Tooltip("severity:N", title="Severity"), alt.Tooltip("reviews:Q", title="Reviews")],
        )
        .properties(height=230)
    )
    draw(chart)
    total_flagged = sum(severity_counts.values())
    st.markdown(
        f"<div class='section-caption'>{total_flagged} flagged in total: "
        f"safety {issue_type_counts.get('safety', 0)}, quality {issue_type_counts.get('quality', 0)}, "
        f"both {issue_type_counts.get('both', 0)}.</div>",
        unsafe_allow_html=True,
    )


def show_overview():
    stats = api_client.get_dashboard_stats()
    overall = stats["overall"]
    _, profile_column = st.columns([5, 1])
    if profile_column.button("Data profile", key="open_profile", width="stretch"):
        show_data_profile()

    cols = st.columns(5)
    cols[0].metric("Reviews", f"{stats['total_reviews']:,}")
    cols[1].metric("Positive %", overall["pct"]["positive"])
    cols[2].metric("Neutral %", overall["pct"]["neutral"])
    cols[3].metric("Negative %", overall["pct"]["negative"])
    cols[4].metric("Flagged reviews", stats["flagged_total"])

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown("**Sentiment by aspect**")
        aspect_chart(stats["aspects"])
    with right:
        st.markdown("**Flagged reviews by severity score**")
        severity_chart(stats["severity_counts"], stats["issue_type_counts"])


def period_count(start_date, end_date, granularity):
    if granularity == "year":
        years = end_date.year - start_date.year + 1
        return max(1, min(years, MAX_TREND_PERIODS))
    if granularity == "month":
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        return max(1, min(months, MAX_TREND_PERIODS))
    weeks = ((end_date - start_date).days // 7) + 1
    return max(1, min(weeks, MAX_TREND_PERIODS))


def trend_frame(series, start_date, granularity):
    if granularity == "year":
        boundary = start_date.strftime("%Y")
    elif granularity == "month":
        boundary = start_date.strftime("%Y-%m")
    else:
        boundary = (start_date - timedelta(days=start_date.weekday())).isoformat()
    rows = [
        {"period": r["period"], "net_sentiment": r["net_sentiment"], "positive": r["pct"]["positive"],
         "negative": r["pct"]["negative"], "reviews": r["n_reviews"]}
        for r in series if r["period"] >= boundary
    ]
    return pd.DataFrame(rows)


def show_trends():
    st.markdown("Choose a product and a date range to see how sentiment moved over time.")

    controls = st.columns([3, 1, 1.3, 1.3], vertical_alignment="bottom")
    picked_product = controls[0].selectbox(
        "Product", api_client.get_product_options(), index=None,
        placeholder="Search a product or choose All products", key="trend_product",
    )
    product = picked_product or "All products"
    granularity = controls[1].selectbox("Group by", ["month", "week", "year"], key="trend_granularity")

    span = api_client.get_product_span(product)
    if span is None:
        st.warning(f"No reviews found for {product}.")
        return
    min_date = pd.Timestamp(span["first"]).date()
    max_date = pd.Timestamp(span["last"]).date()

    if st.session_state.get("trend_product_prev") != product:
        st.session_state.pop("trend_start", None)
        st.session_state.pop("trend_end", None)
        st.session_state["trend_product_prev"] = product

    default_start = max(min_date, max_date - timedelta(days=180))
    start_date = controls[2].date_input(
        "Start date", value=default_start, min_value=min_date, max_value=max_date, key="trend_start",
        help=f"Reviews for this selection begin on {min_date:%d %b %Y}, "
             "so earlier dates cannot be picked.",
    )
    end_date = controls[3].date_input(
        "End date", value=max_date, min_value=min_date, max_value=max_date, key="trend_end",
        help=f"Reviews for this selection end on {max_date:%d %b %Y}, "
             "so later dates cannot be picked.",
    )


    if start_date > end_date:
        st.warning("The start date must be before the end date.")
        return

    result = api_client.get_trends(
        product_name=None if product == "All products" else product,
        granularity=granularity,
        periods=period_count(start_date, end_date, granularity),
        as_of=end_date.isoformat(),
    )
    if "error" in result:
        st.error(result["error"])
        return

    frame = trend_frame(result["series"], start_date, granularity)
    total = int(frame["reviews"].sum()) if not frame.empty else 0
    if total == 0:
        st.info("No reviews match this product and date range. Pick a range inside the dates shown above.")
        return

    positive = (frame["positive"] * frame["reviews"]).sum() / total
    negative = (frame["negative"] * frame["reviews"]).sum() / total
    cols = st.columns(4)
    cols[0].metric("Reviews in range", total)
    cols[1].metric("Positive %", round(positive, 1))
    cols[2].metric("Negative %", round(negative, 1))
    cols[3].metric("Net sentiment", round(positive - negative, 1))

    axis = alt.Axis(labelAngle=-40, labelFontSize=11)
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("**Net sentiment**")
        line = alt.Chart(frame).mark_line(color=TREND_LINE_COLOR, strokeWidth=3, point=alt.OverlayMarkDef(
            color=TREND_POINT_COLOR, filled=True, size=70)).encode(
            x=alt.X("period:N", title=None, sort=None, axis=axis),
            y=alt.Y("net_sentiment:Q", title="Net sentiment", scale=alt.Scale(zero=False, nice=True)),
            tooltip=[alt.Tooltip("period:N", title="Period"),
                     alt.Tooltip("net_sentiment:Q", title="Net sentiment", format=".1f"),
                     alt.Tooltip("positive:Q", title="Positive %", format=".1f"),
                     alt.Tooltip("negative:Q", title="Negative %", format=".1f"),
                     alt.Tooltip("reviews:Q", title="Reviews")],
        ).properties(height=260)
        draw(line)
    with right:
        st.markdown("**Reviews per period**")
        bars = alt.Chart(frame).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("period:N", title=None, sort=None, axis=axis),
            y=alt.Y("reviews:Q", title="Reviews"),
            color=alt.Color("period:N", legend=None, scale=alt.Scale(range=PASTEL_BAR_COLORS)),
            tooltip=[alt.Tooltip("period:N", title="Period"), alt.Tooltip("reviews:Q", title="Reviews")],
        ).properties(height=260)
        draw(bars)

    with st.expander("Numbers behind these charts"):
        render_html_table(frame.rename(columns={
            "period": "Period", "net_sentiment": "Net sentiment", "positive": "Positive %",
            "negative": "Negative %", "reviews": "Reviews"}).style, max_height=300)

    zero_periods = int((frame["reviews"] == 0).sum())
    low_periods = int(((frame["reviews"] > 0) & (frame["reviews"] < LOW_SAMPLE_THRESHOLD)).sum())
    if low_periods or zero_periods:
        parts = []
        if low_periods:
            parts.append(f"{low_periods} period(s) with fewer than 10 reviews")
        if zero_periods:
            parts.append(f"{zero_periods} period(s) with no reviews")
        st.caption(" and ".join(parts).capitalize() + " — treat those points as noisy.")


FLAGGED_COLUMN_WIDTHS = {
    "Review ID": "10%", "Date": "11%", "Stars": "7%", "Product": "22%",
    "Issue": "8%", "Severity": "10%", "What the review says": "32%",
}

def flagged_date(value):
    return pd.Timestamp(value).strftime("%d %b %Y")



def flagged_row(review):
    text = html_escape(" ".join(review["review_text"].split()))
    return (
        f"<tr><td>{review['review_id']}</td>"
        f"<td class='nowrap'>{flagged_date(review['submission_time'])}</td>"
        f"<td>{review['rating']}</td>"
        f"<td>{html_escape(review['product_name'])}</td>"
        f"<td>{html_escape(review['issue_type'])}</td>"
        f"<td>{html_escape(review['severity_level'])}</td>"
        f"<td><details><summary>{text}</summary></details></td></tr>"
    )


def flagged_table_html(reviews):
    cols = "".join(f"<col style='width:{width};'>" for width in FLAGGED_COLUMN_WIDTHS.values())
    head = "".join(f"<th>{name}</th>" for name in FLAGGED_COLUMN_WIDTHS)
    rows = "".join(flagged_row(review) for review in reviews)
    return (
        f"<div class='flag-wrap'><table class='flag-table'><colgroup>{cols}</colgroup>"
        f"<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>"
    )


def show_flagged(limit, heading=True, days=365):
    result = api_client.get_flagged(last_n_days=days, limit=limit, full_text=True)
    if "error" in result:
        st.error(result["error"])
        return
    if heading:
        counts = result["counts_by_level"]
        st.markdown(
            f"<div class='section-caption'>{result['total_matches']} flagged reviews in the last {days} days "
            f"(<span class='severity-badge' style='color:{SEVERITY_COLORS['high']};'>high {counts.get('high', 0)}</span>, "
            f"<span class='severity-badge' style='color:{SEVERITY_COLORS['medium']};'>medium {counts.get('medium', 0)}</span>, "
            f"<span class='severity-badge' style='color:{SEVERITY_COLORS['low']};'>low {counts.get('low', 0)}</span>), "
            f"most severe first.</div>",
            unsafe_allow_html=True,
        )
    if not result["reviews"]:
        st.info("No flagged reviews in this window.")
        return

    st.markdown(flagged_table_html(result["reviews"]), unsafe_allow_html=True)

def render_message(message):
    avatar = ASSISTANT_AVATAR if message["role"] == "assistant" else USER_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


@st.dialog("Clear all history")
def confirm_clear_all(role):
    st.write("This deletes every saved conversation for this role. It does not affect the underlying review data.")
    cancel_col, confirm_col = st.columns(2)
    if cancel_col.button("Cancel", width="stretch"):
        st.rerun()
    if confirm_col.button("Yes, clear everything", type="primary", width="stretch"):
        chat_store.clear_all(role)
        st.session_state.messages = []
        st.session_state.session_id = new_session_id()
        st.rerun()


def render_history_list(role):
    title_col, collapse_col = st.columns([4, 1])
    title_col.markdown("**Conversations**")
    if collapse_col.button("", key="collapse_history", icon=":material/left_panel_close:",
                            type="tertiary"):
        st.session_state.history_collapsed = True
        st.rerun()

    if st.button("New chat", key="new_conversation", icon=":material/add:", width="stretch"):
        start_new_conversation(role)
        st.rerun()

    conversations = chat_store.list_conversations(role)
    if not conversations:
        st.caption("No saved conversations yet.")
    for item in conversations:
        active = item["session_id"] == st.session_state.session_id
        icon = ":material/chat_bubble:" if active else ":material/chat_bubble_outline:"
        open_col, delete_col = st.columns([5, 1])
        if open_col.button(preview(item["title"], HISTORY_LABEL_CHARS), key=f"open_{item['session_id']}",
                           icon=icon, width="stretch"):
            open_conversation(item["session_id"], role)
            st.rerun()
        if delete_col.button("", key=f"del_{item['session_id']}", icon=":material/close:",
                              type="tertiary"):
            chat_store.delete_conversation(item["session_id"])
            if active:
                st.session_state.messages = []
                st.session_state.session_id = new_session_id()
            st.rerun()

    if st.button("Clear all history", key="open_clear_all", icon=":material/delete_sweep:", width="stretch"):
        confirm_clear_all(role)


def render_assistant_header(role):
    if st.session_state.history_collapsed:
        toggle_col, left, clear_col = st.columns([0.6, 4.2, 1.3])
        if toggle_col.button("", key="expand_history", icon=":material/left_panel_open:",
                              type="tertiary"):
            st.session_state.history_collapsed = False
            st.rerun()
    else:
        left, clear_col = st.columns([4.3, 1.3])
    with left:
        caption("Ask a question about the review data below.")
    if clear_col.button("Clear this chat", width="stretch", key="clear_this_chat"):
        chat_store.delete_conversation(st.session_state.session_id)
        st.session_state.messages = []
        st.rerun()


def render_sample_questions(role):
    if "sample_questions_open" not in st.session_state:
        st.session_state.sample_questions_open = not st.session_state.messages
    questions = suggestions.suggest_questions(role, chat_store.answered_questions(role))
    with st.expander("Try a question", expanded=st.session_state.sample_questions_open):
        for index, question in enumerate(questions):
            if st.button(question, key=f"sample_{index}", width="stretch"):
                st.session_state.queued_question = question
                st.session_state.sample_questions_open = False


def scroll_into_view(block="end"):
    components.html(
        f"""
        <script>
        const doc = window.parent.document;
        const el = doc.getElementById("chat-bottom-anchor");
        if (el) {{ el.scrollIntoView({{behavior: "instant", block: "{block}"}}); }}
        </script>
        """,
        height=0,
    )

def status_text(stage):
    if stage["stage"] == STAGE_TOOL_START:
        return TOOL_LABELS.get(stage["detail"], stage["detail"])
    return STAGE_LABELS.get(stage["stage"], "Thinking").format(detail=stage["detail"])


def live_status_html(session_id, started_at, elapsed):
    try:
        stages = api_client.get_progress(session_id)["stages"]
    except requests.RequestException:
        stages = []
    stages = [stage for stage in stages if stage["timestamp"] >= started_at]
    text = status_text(stages[-1]) if stages else "Sending your question"
    return f"<div class='live-status'><span class='dot'></span><span>{text}... ({elapsed:.0f} s)</span></div>"


def ask_with_progress(question, role, session_id, model):
    outcome = {}

    def send():
        try:
            outcome["record"] = api_client.ask_assistant(question, role, session_id, model)
        except requests.RequestException as exc:
            outcome["error"] = exc

    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    started = time.time()
    worker = threading.Thread(target=send, daemon=True)
    worker.start()
    status_box = st.empty()
    while worker.is_alive():
        status_box.markdown(live_status_html(session_id, started_at, time.time() - started), unsafe_allow_html=True)
        time.sleep(PROGRESS_POLL_SEC)
    status_box.empty()
    return outcome.get("record"), outcome.get("error")


def render_conversation(role, model):
    render_sample_questions(role)

    messages = st.session_state.messages
    pending = st.session_state.get("pending_question")
    last_index = len(messages) - 1
    for index, message in enumerate(messages):
        if pending and index == last_index and message["role"] == "user":
            st.markdown('<div id="chat-bottom-anchor"></div>', unsafe_allow_html=True)
        render_message(message)

    if pending:
        scroll_into_view(block="start")
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            record, error = ask_with_progress(pending, role, st.session_state.session_id, model)
        if error:
            st.session_state.pending_question = None
            st.error(f"The assistant request failed: {error}")
            return
        st.session_state.messages.append({"role": "assistant", "content": record["answer"], "record": record})
        st.session_state.pending_question = None
        persist_conversation(role)
        st.rerun()
    else:
        if messages:
            st.markdown('<div id="chat-bottom-anchor"></div>', unsafe_allow_html=True)
        scroll_into_view(block="end")


def show_assistant(role, model):
    if st.session_state.history_collapsed:
        chat_area = st.container()
    else:
        history_column, chat_area = st.columns([1.1, 3.2], gap="large")
        with history_column:
            with st.container(height=PANEL_HEIGHT, border=True):
                render_history_list(role)

    with chat_area:
        render_assistant_header(role)
        with st.container(height=PANEL_HEIGHT):
            render_conversation(role, model)

    question = st.chat_input("Ask about the reviews") or st.session_state.pop("queued_question", None)
    if question and not st.session_state.get("pending_question"):
        st.session_state.messages.append({"role": "user", "content": question, "record": None})
        st.session_state.pending_question = question
        st.rerun()


def numeric(frame, column):
    if column in frame:
        return pd.to_numeric(frame[column], errors="coerce").fillna(0)
    return pd.Series(0, index=frame.index)


def preview(text, width=90):
    text = " ".join(str(text or "").split())
    return text if len(text) <= width else text[: width - 3] + "..."


def audit_summary_table(frame):
    tokens = numeric(frame, "prompt_tokens") + numeric(frame, "completion_tokens")
    return pd.DataFrame({
        "Time": pd.to_datetime(frame["timestamp"], errors="coerce").dt.strftime("%d %b %H:%M"),
        "Role": frame["role"].map(ROLE_LABELS),
        "Question": frame["question"].map(lambda t: preview(t, 70)),
        "Status": frame["status"],
        "Seconds": numeric(frame, "latency_sec").round(2).map(lambda v: f"{v:.2f}"),
        "Tokens": tokens.astype(int),
    })


def show_audit(role):
    session_ids = [st.session_state.session_id] + [c["session_id"] for c in chat_store.list_conversations(role)]
    records = api_client.get_audit_logs(role, ",".join(session_ids))
    if not records:
        st.info("No interactions logged yet. Ask a question in the Assistant tab and it will appear here.")
        return

    frame = pd.DataFrame(records)
    if role == "brand_manager":
        labels = {label: name for name, label in ROLE_LABELS.items()}
        picked = st.segmented_control(
            "Show audit of", ["Both"] + list(labels), default="Both", key="audit_role_filter",) or "Both"

        if picked != "Both":
            frame = frame[frame["role"] == labels[picked]]
            if frame.empty:
                st.info(f"No interactions logged for the {picked.lower()} yet.")
                return


    if "answer" not in frame.columns:
        render_html_table(audit_summary_table(frame).iloc[::-1].style, max_height=380)
        return


    answered = frame[frame["status"] == "answered"]
    cols = st.columns(4)
    cols[0].metric("Requests", len(frame))
    cols[1].metric("Answered", len(answered))
    cols[2].metric("Average seconds", round(numeric(answered, "latency_sec").mean(), 2) if len(answered) else 0)

    render_html_table(audit_summary_table(frame).iloc[::-1].head(30).style, max_height=460)

PROFILE_COLUMN_WIDTHS = {
    "Column": "27%", "Type": "6%", "Source": "6%", "Null count": "6%", "Populated": "7%",
    "Distinct": "7%", "Minimum": "8%", "Maximum": "8%", "Max length": "7%", "Examples": "18%",
}


def profile_header_html(profile):
    items = [
        ("Dataset", html_escape(profile["dataset"])),
        ("Source", f"<a href='{html_escape(profile['source_url'])}' target='_blank' rel='noopener noreferrer'>"
                   f"{html_escape(profile['source'])}</a>"),
        ("File", html_escape(profile["file"])),
        ("Rows and columns", f"{profile['row_count']:,} rows, {profile['column_count']} columns"),
        ("Date statistics collected", html_escape(profile["generated_at"])),
    ]
    cells = "".join(
        f"<div class='profile-item'><div class='label'>{label}</div><div class='value'>{value}</div></div>"
        for label, value in items
    )
    return f"<div class='profile-head'>{cells}</div>"


def profile_row(column):
    if column["name"] in PROFILE_SENSITIVE_COLUMNS:
        examples = "<span class='muted'>hidden for privacy</span>"
    elif column["examples"]:
        examples = "".join(f"<div>{html_escape(value)}</div>" for value in column["examples"])
    else:
        examples = "-"
    max_length = "Not a string" if column["kind"] != "text" else (column["max_length"] or "-")
    return (
        f"<tr><td><div class='name'>{html_escape(column['name'])}</div>"
        f"<div class='desc'>{html_escape(column['description'])}</div></td>"
        f"<td>{column['kind']}</td><td>{column['source']}</td>"
        f"<td>{column['null_count']:,}</td><td>{column['percent_populated']:g}%</td>"
        f"<td>{column['distinct_count']:,}</td>"
        f"<td>{html_escape(column['minimum'] or '-')}</td><td>{html_escape(column['maximum'] or '-')}</td>"
        f"<td>{max_length}</td><td>{examples}</td></tr>"
    )


def profile_table_html(columns):
    cols = "".join(f"<col style='width:{width};'>" for width in PROFILE_COLUMN_WIDTHS.values())
    head = "".join(f"<th>{name}</th>" for name in PROFILE_COLUMN_WIDTHS)
    rows = "".join(profile_row(column) for column in columns)
    return (
        f"<div class='profile-scroll'><table class='profile-table'><colgroup>{cols}</colgroup>"
        f"<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>"
    )



@st.dialog("Data profile", width="large")
def show_data_profile():
    try:
        profile = api_client.get_data_profile()
    except requests.RequestException as exc:
        st.error(f"Could not load the data profile. Is the backend running? ({exc})")
        return

    st.markdown(profile_header_html(profile), unsafe_allow_html=True)
    st.markdown(profile_table_html(profile["columns"]), unsafe_allow_html=True)



def main():
    init_state()
    role, model = render_sidebar()

    if st.session_state.get("last_role") != role:
        persist_conversation(st.session_state.get("last_role") or role)
        st.session_state.session_id = new_session_id()
        st.session_state.messages = []
        st.session_state.last_role = role
        st.session_state.section = None

    if st.session_state.get("last_model") not in (None, model):
        start_new_conversation(role)
    st.session_state.last_model = model

    st.title("Review Intelligence")

    sections = BRAND_SECTIONS if role == "brand_manager" else SUPPORT_SECTIONS
    section = render_nav(sections)

    try:
        if section == "Overview":
            show_overview()
        elif section == "Trends":
            show_trends()
        elif section == "Flagged reviews":
            show_flagged(30)
        elif section == "Assistant":
            show_assistant(role, model)
        elif section == "Audit log":
            show_audit(role)
    except requests.RequestException as exc:
        st.error(f"Could not load this section. Is the backend running? ({exc})")


main()


