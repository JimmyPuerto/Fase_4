"""
SOFTWARE FJ - Sistema de gestion de clientes, servicios y reservas
Jimmy Puerto Gomez
------------------------------------------------------------------
Programa hecho con Programacion Orientada a Objetos (sin base de datos).
Los datos viven en listas dentro de la memoria y solo se usa un archivo
para guardar los logs (eventos y errores).
---------------------------------------------------------------
SEGMENTO 1 - Excepciones personalizadas y configuracion de logs
---------------------------------------------------------------
Aqui va la base del manejo de errores del sistema:
 - Se configura el archivo de logs (unica cosa que se guarda en archivo).
 - Se crean las excepciones propias, todas heredan de SoftwareFJError. 
 (`ClienteInvalidoError`, `ServicioInvalidoError`, `ServicioNoDisponibleError`,
  `ReservaInvalidaError`, `OperacionNoPermitidaError`, `CalculoInconsistenteError`).
 - Se configura un `FileHandler` para guardar eventos y errores en `logs_software_fj.log`.
 - Con un solo `except SoftwareFJError` se atrapan todos los errores propios.
"""

import logging

# ---------------------------------------------------------------
# CONFIGURACION DEL ARCHIVO DE LOGS
# ---------------------------------------------------------------
manejador = logging.FileHandler("logs_software_fj.log", encoding="utf-8")
manejador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

log = logging.getLogger("SoftwareFJ")
log.setLevel(logging.INFO)
log.addHandler(manejador)


# ---------------------------------------------------------------
# EXCEPCIONES PERSONALIZADAS
# ---------------------------------------------------------------
class SoftwareFJError(Exception):
    """Excepcion base del sistema (todas las demas heredan de esta)."""


class ClienteInvalidoError(SoftwareFJError):
    """Datos del cliente incorrectos."""


class ServicioInvalidoError(SoftwareFJError):
    """Parametros del servicio incorrectos."""


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio existe pero no esta disponible."""


class ReservaInvalidaError(SoftwareFJError):
    """La reserva no se pudo crear o procesar."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se intento hacer algo que el estado actual no permite."""


class CalculoInconsistenteError(SoftwareFJError):
    """El calculo de un costo dio algo que no tiene sentido."""
