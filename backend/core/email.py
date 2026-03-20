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


def create_content_email_html(content: dict, client_name: str, recommendation_details: dict = None) -> str:
    """Create HTML email for content delivery with full articles.

    Args:
        content: The content record with articles in all languages.
        client_name: Client name for greeting.
        recommendation_details: Original recommendation details for context.
    """
    details = recommendation_details or {}

    # Build the "Why we wrote this" section
    keyword = details.get('keyword', content.get('keyword', 'N/A'))
    intent = details.get('intent', 'informational')
    search_volume = details.get('search_volume', 'N/A')
    notes = details.get('notes', '')
    suggested_topic = details.get('suggested_topic', '')
    opportunity_type = details.get('opportunity_type', '')
    current_position = details.get('current_position')

    # Map opportunity types to readable labels
    opportunity_labels = {
        'quick_win': 'Quick Win (Position 4-10)',
        'low_hanging_fruit': 'Low Hanging Fruit (Position 11-20)',
        'ctr_opportunity': 'CTR Improvement Opportunity',
        'striking_distance': 'Striking Distance (Position 21-30)',
    }
    opportunity_label = opportunity_labels.get(opportunity_type, opportunity_type.replace('_', ' ').title())

    # Build context explanation
    context_parts = []
    if current_position:
        context_parts.append(f"Currently ranking at position #{current_position:.0f}")
    if search_volume and search_volume != 'N/A':
        context_parts.append(f"~{search_volume} monthly searches")
    if intent:
        context_parts.append(f"{intent.title()} intent")

    context_line = " • ".join(context_parts) if context_parts else ""

    # Get translated keywords
    keyword_en = content.get('keyword_en', keyword)
    keyword_fr = content.get('keyword_fr', keyword)
    keyword_nl = content.get('keyword_nl', keyword)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #1a1a1a; background: #ffffff; }}
            .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #3B82F6, #8B5CF6); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
            .header h1 {{ margin: 0; color: white; }}
            .header p {{ margin: 10px 0 0 0; opacity: 0.9; color: white; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .content p {{ color: #1a1a1a; }}
            .context-box {{ background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 8px; padding: 20px; margin: 20px 0; }}
            .context-box h3 {{ margin-top: 0; color: #4338ca; }}
            .context-box p {{ color: #1e1b4b; margin: 8px 0; }}
            .context-box .label {{ font-weight: 600; color: #6366f1; }}
            .article-section {{ background: white; padding: 25px; border-radius: 8px; margin: 25px 0; border: 1px solid #e2e8f0; }}
            .article-section h2 {{ color: #1e40af; margin-top: 0; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
            .language-badge {{ display: inline-block; background: #3b82f6; color: white; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; margin-bottom: 15px; }}
            .language-badge.fr {{ background: #dc2626; }}
            .language-badge.nl {{ background: #f97316; }}
            .meta-info {{ background: #f1f5f9; padding: 12px 16px; border-radius: 6px; margin-bottom: 15px; font-size: 14px; color: #475569; }}
            .meta-info strong {{ color: #1e293b; }}
            .article-content {{ color: #1a1a1a; font-size: 15px; line-height: 1.8; white-space: pre-wrap; }}
            .article-content h1, .article-content h2, .article-content h3 {{ color: #1e293b; }}
            .copy-hint {{ background: #fef3c7; border: 1px solid #fcd34d; border-radius: 6px; padding: 12px 16px; font-size: 13px; color: #92400e; margin-top: 10px; }}
            .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📝 New SEO Article Drafts</h1>
                <p>3 language versions ready for review</p>
            </div>
            <div class="content">
                <p style="color: #1a1a1a;">Hi {client_name},</p>

                <!-- Why We Wrote This Section -->
                <div class="context-box">
                    <h3>📊 Why We Wrote This Article</h3>
                    <p><span class="label">Target Keyword:</span> {keyword}</p>
                    <p><span class="label">Opportunity Type:</span> {opportunity_label}</p>
                    {f'<p><span class="label">Stats:</span> {context_line}</p>' if context_line else ''}
                    {f'<p><span class="label">Topic Angle:</span> {suggested_topic}</p>' if suggested_topic else ''}
                    {f'<p><span class="label">Why:</span> {notes}</p>' if notes else ''}
                </div>

                <p style="color: #1a1a1a;">Below are <strong>3 article drafts</strong> ready to copy-paste. Each article is optimized for the target keyword in its respective language.</p>

                <!-- English Article -->
                <div class="article-section">
                    <span class="language-badge">🇬🇧 ENGLISH</span>
                    <div class="meta-info">
                        <strong>Target Keyword:</strong> {keyword_en}<br>
                        <strong>Meta Description:</strong> {content.get('meta_description_en', 'N/A')}
                    </div>
                    <h2>{content.get('title_en', 'Article Title')}</h2>
                    <div class="article-content">{content.get('content_en', 'Content not available.')}</div>
                    <div class="copy-hint">💡 Copy everything from the title above to create your blog post</div>
                </div>

                <!-- French Article -->
                <div class="article-section">
                    <span class="language-badge fr">🇫🇷 FRANÇAIS</span>
                    <div class="meta-info">
                        <strong>Mot-clé cible:</strong> {keyword_fr}<br>
                        <strong>Méta description:</strong> {content.get('meta_description_fr', 'N/A')}
                    </div>
                    <h2>{content.get('title_fr', "Titre de l'article")}</h2>
                    <div class="article-content">{content.get('content_fr', 'Contenu non disponible.')}</div>
                    <div class="copy-hint">💡 Copiez tout depuis le titre ci-dessus pour créer votre article de blog</div>
                </div>

                <!-- Dutch Article -->
                <div class="article-section">
                    <span class="language-badge nl">🇳🇱 NEDERLANDS</span>
                    <div class="meta-info">
                        <strong>Doelzoekwoord:</strong> {keyword_nl}<br>
                        <strong>Meta beschrijving:</strong> {content.get('meta_description_nl', 'N/A')}
                    </div>
                    <h2>{content.get('title_nl', 'Artikel Titel')}</h2>
                    <div class="article-content">{content.get('content_nl', 'Inhoud niet beschikbaar.')}</div>
                    <div class="copy-hint">💡 Kopieer alles vanaf de titel hierboven om je blogpost te maken</div>
                </div>

                <div class="footer">
                    <p>Generated by AI Ops • Your Marketing Intelligence Platform</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
