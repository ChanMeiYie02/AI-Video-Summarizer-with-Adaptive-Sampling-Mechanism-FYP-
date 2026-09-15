import os
import datetime
from fpdf import FPDF

def to_latin1(text):
    """Clean and encode text to latin-1 to avoid standard PDF font encoding crashes."""
    replacements = {
        "\u201c": '"',  # Left double quote
        "\u201d": '"',  # Right double quote
        "\u2018": "'",  # Left single quote
        "\u2019": "'",  # Right single quote
        "\u2013": "-",  # En dash
        "\u2014": "-",  # Em dash
        "\u2022": "-",  # Bullet point
        "\u2026": "...", # Ellipsis
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', errors='replace').decode('latin-1')

def format_time_srt(seconds):
    """Format seconds float into standard SRT timestamp format: HH:MM:SS,mmm"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int(round((seconds - int(seconds)) * 1000))
    if msecs >= 1000:
        msecs = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

def export_to_srt(transcripts):
    """Convert pipeline transcripts into standard SubRip Subtitle (.srt) format."""
    srt_lines = []
    for i, t in enumerate(transcripts, 1):
        start_sec = t.get("start", t.get("start_sec", 0))
        end_sec = t.get("end", t.get("end_sec", start_sec))
        text = t.get("text", "").strip()
        
        start_str = format_time_srt(start_sec)
        end_str = format_time_srt(end_sec)
        
        srt_lines.append(f"{i}")
        srt_lines.append(f"{start_str} --> {end_str}")
        srt_lines.append(f"{text}\n")
    return "\n".join(srt_lines)

def export_to_markdown(overall_summary, summaries, keyframes, video_name="Video"):
    """Format final summaries, chapters, and keyframes into a clean Markdown study guide."""
    md = []
    md.append(f"# 📖 Study Guide: {video_name}")
    md.append(f"\n*Generated on: {datetime.date.today().strftime('%B %d, %Y')}*\n")
    md.append("## 📹 Video Executive Summary")
    md.append(overall_summary)
    md.append("\n---\n")
    md.append("## 🗂️ Chapter Outlines")
    
    for topic in summaries:
        title = topic.get("title", f"Topic {topic.get('subtopic_id')}").replace("TITLE:", "").strip()
        desc = topic.get("description", "No description provided.").replace("DESCRIPTION:", "").strip()
        summary = topic.get("summary", "")
        
        md.append(f"### 📌 {title}")
        md.append(f"**Brief:** *{desc}*")
        if summary:
            clean_summary = summary.replace("SUMMARY:", "").strip()
            md.append(f"\n{clean_summary}\n")
            
    if keyframes:
        md.append("\n---\n")
        md.append("## 🖼️ Visual Keyframes & Milestones")
        for kf in keyframes:
            timestamp_sec = kf.get('timestamp_sec', 0.0)
            frame_idx = kf.get('frame_index', 0)
            filename = kf.get('filename', '')
            
            mins = int(timestamp_sec // 60)
            secs = int(timestamp_sec % 60)
            time_str = f"{mins}:{secs:02d}"
            
            md.append(f"- **Frame {frame_idx}** at **{time_str}** (`{filename}`)")
            
    return "\n".join(md)

class VideoSummaryPDF(FPDF):
    """Custom FPDF subclass with page headers and footers."""
    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "Video Summarization Report", align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(220, 220, 220)
            self.line(10, 18, 200, 18)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def export_to_pdf(overall_summary, summaries, keyframes, video_meta, frames_dir):
    """Generate a styled PDF summary report containing metadata, summaries, and keyframe images."""
    pdf = VideoSummaryPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ─── COVER PAGE ───
    pdf.add_page()
    pdf.set_font("helvetica", "B", 26)
    pdf.set_text_color(23, 78, 166)  # Deep blue
    pdf.ln(45)
    
    title_text = to_latin1(video_meta.get('name', 'N/A'))
    pdf.cell(0, 15, "AI Video Summarization", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(15, 31, 61)   # Charcoal
    pdf.cell(0, 15, "Executive Summaries & Visual Outlines", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Accenting blue divider line
    pdf.set_draw_color(47, 123, 229)
    pdf.set_line_width(1.2)
    pdf.line(40, 100, 170, 100)
    
    pdf.ln(45)
    # Metadata Block
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(91, 111, 149)  # Soft slate
    pdf.cell(0, 8, to_latin1(f"Video Source: {title_text}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, to_latin1(f"Duration: {video_meta.get('duration', 'N/A')}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, to_latin1(f"Processed At: {video_meta.get('processed_at', 'N/A')}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, to_latin1(f"Generated Report: {datetime.date.today().strftime('%Y-%m-%d')}"), align="C", new_x="LMARGIN", new_y="NEXT")
    
    # ─── SECTION 1: EXECUTIVE SUMMARY ───
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(23, 78, 166)
    pdf.cell(0, 10, "1. Executive Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(15, 31, 61)
    
    clean_summary = overall_summary.replace("**", "").replace("*", "").replace("#", "")
    pdf.multi_cell(0, 6, to_latin1(clean_summary))
    pdf.ln(10)
    
    # ─── SECTION 2: CHAPTER OUTLINES ───
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(23, 78, 166)
    pdf.cell(0, 10, "2. Chapter Outlines", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    for topic in summaries:
        title = topic.get("title", f"Topic {topic.get('subtopic_id')}").replace("TITLE:", "").strip()
        desc = topic.get("description", "No description provided.").replace("DESCRIPTION:", "").strip()
        summary = topic.get("summary", "")
        
        # Check space before adding block to prevent awkward overlaps
        if pdf.get_y() > 240:
            pdf.add_page()
            
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(23, 78, 166)
        pdf.cell(0, 8, to_latin1(f"- {title}"), new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(91, 111, 149)
        pdf.multi_cell(0, 5, to_latin1(f"Description: {desc}"))
        
        if summary:
            pdf.ln(1)
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(15, 31, 61)
            clean_sub_summary = summary.replace("SUMMARY:", "").replace("**", "").replace("*", "").replace("#", "").strip()
            pdf.multi_cell(0, 5, to_latin1(clean_sub_summary))
        
        pdf.ln(6)
        
    # ─── SECTION 3: VISUAL KEYFRAME MILESTONES ───
    if keyframes:
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(23, 78, 166)
        pdf.cell(0, 10, "3. Visual Keyframe Milestones", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        
        col = 0
        x_coords = [10, 110]
        
        for kf in keyframes:
            filename = kf.get('filename', '')
            frame_path = os.path.join(frames_dir, filename)
            timestamp_sec = kf.get('timestamp_sec', 0.0)
            frame_idx = kf.get('frame_index', 0)
            
            mins = int(timestamp_sec // 60)
            secs = int(timestamp_sec % 60)
            time_str = f"{mins}:{secs:02d}"
            
            if os.path.exists(frame_path):
                # Page break check
                if pdf.get_y() > 220:
                    pdf.add_page()
                    col = 0
                    
                current_y = pdf.get_y()
                x = x_coords[col]
                
                # Render Image (85mm width, 48mm height matches 16:9 ratio)
                try:
                    pdf.image(frame_path, x=x, y=current_y, w=85, h=48)
                except Exception:
                    pdf.rect(x, current_y, 85, 48)
                    pdf.text(x+5, current_y+25, "[Image Render Error]")
                    
                # Render Timestamp label below image
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(15, 31, 61)
                label_y = current_y + 51
                pdf.text(x, label_y, to_latin1(f"Frame {frame_idx} @ {time_str}"))
                
                # Flip columns
                if col == 0:
                    col = 1
                else:
                    col = 0
                    pdf.set_y(label_y + 8)
                    
        # Make sure cursor is shifted down for any trailing odd column element
        if col == 1:
            pdf.set_y(pdf.get_y() + 59)
            
    return bytes(pdf.output())
