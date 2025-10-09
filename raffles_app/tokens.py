"""
Genera tokens únicos para la activación de cuentas de usuario.
Se basa en el sistema de generación de tokens de restablecimiento de contraseña
de Django, adaptado para verificar el estado de activación del usuario.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Clase personalizada para generar y validar tokens de activación de cuenta.
    El token se construye a partir del ID del usuario, el timestamp y
    el estado `is_active`, de modo que si el usuario ya ha activado
    su cuenta, el token anterior queda automáticamente invalidado.
    """
    def _make_hash_value(self, user, timestamp):
        # Incluye el estado activo del usuario para invalidar el token tras activación
        return f"{user.pk}{timestamp}{user.is_active}"

# Instancia única reutilizable en las vistas
account_activation_token = AccountActivationTokenGenerator()
