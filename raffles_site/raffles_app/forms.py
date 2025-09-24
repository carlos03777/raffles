from django import forms

class TicketPurchaseForm(forms.Form):
    number = forms.IntegerField(
        required=False,
        min_value=1,
        label="Número de boleta (opcional)",
        help_text="Déjalo vacío para asignación aleatoria."
    )
