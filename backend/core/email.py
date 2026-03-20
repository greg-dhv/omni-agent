"""Email service for AI Ops Platform."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


async def send_email_sendgrid(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
) -> bool:
    """Send email using SendGrid API."""
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content

    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        raise ValueError("SENDGRID_API_KEY not set")

    sg = sendgrid.SendGridAPIClient(api_key=api_key)

    from_email = from_email or os.environ.get("EMAIL_FROM", "noreply@example.com")
    from_name = from_name or os.environ.get("EMAIL_FROM_NAME", "AI Ops")

    message = Mail(
        from_email=Email(from_email, from_name),
        to_emails=To(to_email, to_name),
        subject=subject,
        html_content=Content("text/html", html_content),
    )

    try:
        response = sg.send(message)
        return response.status_code in (200, 201, 202)
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False


async def send_email_smtp(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
) -> bool:
    """Send email using SMTP."""
    import aiosmtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        raise ValueError("SMTP_USER and SMTP_PASSWORD must be set")

    from_email = from_email or smtp_user
    from_name = from_name or os.environ.get("EMAIL_FROM_NAME", "AI Ops")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{from_name} <{from_email}>"
    message["To"] = f"{to_name} <{to_email}>"

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True,
        )
        return True
    except Exception as e:
        print(f"SMTP error: {e}")
        return False


async def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    provider: str = "sendgrid",
) -> bool:
    """Send email using configured provider."""
    if provider == "sendgrid":
        return await send_email_sendgrid(
            to_email, to_name, subject, html_content, from_email, from_name
        )
    else:
        return await send_email_smtp(
            to_email, to_name, subject, html_content, from_email, from_name
        )


def create_content_email_html(content: dict, client_name: str) -> str:
    """Create HTML email for content delivery."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #3B82F6, #8B5CF6); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .article {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3B82F6; }}
            .language-tag {{ display: inline-block; background: #e2e8f0; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin-right: 8px; }}
            .cta {{ display: inline-block; background: #3B82F6; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin-top: 20px; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0;">New Content Ready</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">AI-generated article for your review</p>
            </div>
            <div class="content">
                <p>Hi {client_name},</p>
                <p>A new blog article has been created based on your SEO strategy:</p>

                <div class="article">
                    <h2 style="margin-top: 0;">{content.get('title_en', content.get('keyword', 'New Article'))}</h2>
                    <p><strong>Target Keyword:</strong> {content.get('keyword', 'N/A')}</p>
                    <div>
                        <span class="language-tag">English</span>
                        <span class="language-tag">French</span>
                        <span class="language-tag">Dutch</span>
                    </div>
                </div>

                <p>The article is available in English, French, and Dutch. You can view and download all versions from your dashboard.</p>

                <a href="#" class="cta">View in Dashboard</a>

                <div class="footer">
                    <p>This email was sent by AI Ops - your marketing intelligence platform.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
