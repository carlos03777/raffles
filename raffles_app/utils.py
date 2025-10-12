# raffles_app/utils.py
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from decouple import config


def send_activation_email(to_email, subject, html_content):
    """
    Envía un correo de activación usando la API de Brevo.
    Requiere que la variable de entorno BREVO_API_KEY esté configurada.
    """
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = config("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    sender = {"name": "Raffles", "email": "no-reply@raffles.com"}
    to = [{"email": to_email}]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        sender=sender,
        subject=subject,
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Correo enviado correctamente a {to_email}")
    except ApiException as e:
        print(f"❌ Error enviando correo a {to_email}: {e}")
