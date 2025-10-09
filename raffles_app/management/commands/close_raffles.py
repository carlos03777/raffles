# from django.core.management.base import BaseCommand
# from django.utils import timezone

# from raffles_app.models import Raffle


# class Command(BaseCommand):
#     help = "Cierra rifas vencidas y asigna ganador automáticamente"

#     def handle(self, *args, **kwargs):
#         now = timezone.now()
#         raffles = Raffle.objects.filter(status="open", ends_at__lte=now)

#         for raffle in raffles:
#             self.stdout.write(f"🎯 Cerrando rifa {raffle.id} - {raffle.motorcycle}")
#             try:
#                 if not raffle.seed_commitment:
#                     raffle.create_commit()

#                 winner = raffle.pick_winner_commit_reveal()
#                 self.stdout.write(self.style.SUCCESS(
#                     f"Ganador asignado: {winner.user.username} con ticket #{winner.number}"
#                 ))
#             except Exception as e:
#                 self.stderr.write(self.style.ERROR(f"Error con rifa {raffle.id}: {str(e)}"))

from django.core.management.base import BaseCommand
from django.utils import timezone

from raffles_app.models import Raffle


class Command(BaseCommand):
    help = "Cierra rifas vencidas y asigna ganador automáticamente"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        raffles = Raffle.objects.filter(status="open", ends_at__lte=now)

        for raffle in raffles:
            self.stdout.write(f"🎯 Procesando rifa {raffle.id} - {raffle.motorcycle}")

            try:
                # Si no hay commit, lo generamos antes de cerrar
                if not raffle.seed_commitment:
                    raffle.create_commit()

                winner = raffle.close_if_expired()

                if winner:
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Rifa {raffle.id} finalizada. Ganador: {winner.user.username} con ticket #{winner.number}"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"⚠️ Rifa {raffle.id} cerrada sin participantes"
                    ))

            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"❌ Error en rifa {raffle.id}: {str(e)}"
                ))
