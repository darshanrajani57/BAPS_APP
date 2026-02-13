from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

def generate_pdf(text_lines, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 40
    for line in text_lines:
        c.drawString(40, y, line)
        y -= 16
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()


def generate_session_pdf_detailed(session_id, session_data, members_data, assignments_data, output_path):
    """Generate a detailed PDF report grouped by Sampark Karyakar with A/P attendance markers"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#000000'),
        spaceAfter=6,
        alignment=1  # center
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#FFFFFF'),
        backColor=colors.HexColor('#000000'),
        alignment=0,
        spaceAfter=4
    )
    
    summary_style = ParagraphStyle(
        'SummaryHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#FFFFFF'),
        backColor=colors.HexColor('#000000'),
        alignment=1,
        spaceAfter=4
    )

    # Add title
    from reportlab.platypus import Paragraph
    from datetime import datetime
    
    # Convert date format from YYYY-MM-DD to DD/MM/YYYY
    date_str = session_data.get('date', 'N/A')
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
    except:
        formatted_date = date_str
    
    elements.append(Paragraph(f"Sabha Attendance Report - {formatted_date}", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Build attendance dictionary
    attendance = session_data.get('attendance', {})
    
    # Group members by sampark karyakar and track counts by type
    grouped_data = {}
    type_summary = {}
    
    for yuvak_name, member_info in members_data.items():
        assignment = assignments_data.get(yuvak_name, {})
        sampark = assignment.get('sampark', 'Unassigned')
        
        # Handle both old format (string) and new format (dict with status and time)
        attendance_info = attendance.get(yuvak_name, {})
        if isinstance(attendance_info, str):
            # Old format compatibility
            attendance_status = attendance_info
            arrival_time = None
        else:
            # New format with timing
            attendance_status = attendance_info.get('status', 'Absent')
            arrival_time = attendance_info.get('time', None)
        
        if sampark not in grouped_data:
            grouped_data[sampark] = []
        
        grouped_data[sampark].append({
            'name': yuvak_name,
            'phone': member_info.get('Yuvak Phone No.', member_info.get('Phone', 'N/A')),
            'status': attendance_status,
            'time': arrival_time,
            'type': member_info.get('Type', 'Yuvak')
        })
        
        # Track counts by member type
        member_type = member_info.get('Type', 'Yuvak')
        if member_type not in type_summary:
            type_summary[member_type] = {'Present': 0, 'Absent': 0}
        type_summary[member_type][attendance_status] += 1

    # Generate tables for each Sampark Karyakar
    for sampark_name in sorted(grouped_data.keys()):
        members_list = grouped_data[sampark_name]
        
        # Display name - use "Unassigned" if empty
        display_name = sampark_name if sampark_name and str(sampark_name).strip() else "Unassigned"
        
        # Get status of the sampark karyakar (if they are in the members list)
        sampark_status = 'A'  # Default to Absent
        for member in members_list:
            # Assuming the first member or we need to find the sampark karyakar themselves
            # For now, if any in group is present, we'll show P
            if member['status'] == 'Present':
                sampark_status = 'P'
                break
        
        # If all are absent, keep A
        if sampark_status == 'A':
            for member in members_list:
                if member['status'] == 'Absent':
                    sampark_status = 'A'
        
        # Header with sampark/karyakar name and status letter (black background)
        header_text = f"{display_name}  ({sampark_status})"
        header_para = Paragraph(header_text, header_style)
        header_table = Table([[header_para]], colWidths=[7.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.1*inch))

        # Build data table (yellow headers)
        table_data = [['Yuvak Name', 'Mobile Number', 'Status', 'Arrival Time']]
        
        for member in members_list:
            status_marker = 'P' if member['status'] == 'Present' else 'A'
            time_str = member.get('time', '') or '-'
            table_data.append([
                member['name'],
                member['phone'],
                status_marker,
                time_str
            ])

        # Create table with styling
        table = Table(table_data, colWidths=[3*inch, 2*inch, 0.8*inch, 1.7*inch])
        table.setStyle(TableStyle([
            # Header row (yellow background)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFFF00')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#000000')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#000000')),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

    # Add Summary Section
    elements.append(Spacer(1, 0.2*inch))
    summary_header = Paragraph("ATTENDANCE SUMMARY", summary_style)
    summary_header_table = Table([[summary_header]], colWidths=[7.5*inch])
    summary_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#000000')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_header_table)
    elements.append(Spacer(1, 0.15*inch))

    # Build summary table grouped by member type (Category)
    summary_data = [['Category', 'Present', 'Absent', 'Total']]
    total_present = 0
    total_absent = 0
    
    # Sort type names for consistent ordering
    type_order = ['Sanchalak', 'Sampark Karyakar', 'Karyakar', 'Yuvak']
    for member_type in type_order:
        if member_type in type_summary:
            present_count = type_summary[member_type]['Present']
            absent_count = type_summary[member_type]['Absent']
            total = present_count + absent_count
            total_present += present_count
            total_absent += absent_count
            
            summary_data.append([
                member_type,
                str(present_count),
                str(absent_count),
                str(total)
            ])
    
    # Add any other types not in the predefined order
    for member_type in sorted([str(t) for t in type_summary.keys() if t and str(t) != 'nan']):
        if member_type not in type_order:
            present_count = type_summary.get(member_type, {}).get('Present', 0)
            absent_count = type_summary.get(member_type, {}).get('Absent', 0)
            
            # Try to get from type_summary using original key if it exists
            for orig_key in type_summary.keys():
                if str(orig_key) == member_type:
                    present_count = type_summary[orig_key]['Present']
                    absent_count = type_summary[orig_key]['Absent']
                    break
            
            total = present_count + absent_count
            total_present += present_count
            total_absent += absent_count
            
            summary_data.append([
                member_type,
                str(present_count),
                str(absent_count),
                str(total)
            ])
    
    # Add total row
    summary_data.append([
        'TOTAL',
        str(total_present),
        str(total_absent),
        str(total_present + total_absent)
    ])

    # Create summary table with styling
    summary_table = Table(summary_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        # Header row (yellow background)
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFFF00')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#000000')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#FFFFFF')),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.HexColor('#000000')),
        ('ALIGN', (0, 1), (-1, -2), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 6),
        ('TOPPADDING', (0, 1), (-1, -2), 6),
        
        # Total row (bold, gray background)
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D3D3D3')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#000000')),
        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        
        # Borders
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#000000')),
    ]))
    
    elements.append(summary_table)

    # Build PDF
    doc.build(elements)
