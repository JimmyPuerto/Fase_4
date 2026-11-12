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

# ===============================================================
# SEGMENTO 2 - Clase abstracta EntidadBase y clase Cliente
# ===============================================================
# - EntidadBase: clase abstracta general (da un id automatico y obliga
#   a implementar describir()).  -> ABSTRACCION
# - Cliente: hereda de EntidadBase.  -> HERENCIA
# - Cliente usa atributos privados con @property y valida nombre, correo
#   y telefono en los setters.  -> ENCAPSULACION
# - Si un dato es invalido se ejecuta ClienteInvalidoError.

import re
from abc import ABC, abstractmethod

# ---------------------------------------------------------------
# CLASE ABSTRACTA GENERAL
# ---------------------------------------------------------------
class EntidadBase(ABC):
    """Representa cualquier entidad del sistema (cliente, servicio...)."""

    _contador = 0  # para dar ids automaticos

    def __init__(self):
        EntidadBase._contador += 1
        self._id = EntidadBase._contador

    @property
    def id(self):
        return self._id

    @abstractmethod
    def describir(self):
        """Cada entidad tiene que saber describirse."""

# ---------------------------------------------------------------
# CLIENTE
# ---------------------------------------------------------------
class Cliente(EntidadBase):
    def __init__(self, nombre, correo, telefono):
        super().__init__()
        # Las validaciones se hacen en los setters (esto es encapsulacion)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

@property
    def nombre(self):
        return self.__nombre

@nombre.setter
def nombre(self, valor):
 if not isinstance(valor, str) or len(valor.strip()) < 3:
        raise ClienteInvalidoError("El nombre debe ser texto de minimo de 3 caracteres.")
        if any(ch.isdigit() for ch in valor):
            raise ClienteInvalidoError("El nombre no puede tener numeros.")
        self.__nombre = valor.strip().title()

@property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not isinstance(valor, str) or not re.match(patron, valor):
            raise ClienteInvalidoError(f"Correo invalido: '{valor}'.")
        self.__correo = valor.lower()

@property
def telefono(self):
 return self.__telefono

@telefono.setter
    def telefono(self, valor):
        if not isinstance(valor, str) or not valor.isdigit() or len(valor) != 10:
            raise ClienteInvalidoError("El telefono debe tener exactamente 10 digitos.")
        self.__telefono = valor

    def describir(self):
        return f"Cliente #{self.id}: {self.nombre} | {self.correo} | Tel: {self.telefono}"

# ===============================================================
# SEGMENTO 3 - Clase abstracta Servicio y servicios especializados
# ===============================================================
# - Servicio (abstracta): tiene los datos comunes (nombre, tarifa,
#   disponibilidad) y el calculo del costo.
# - ReservaSala, AlquilerEquipo y Asesoria heredan de Servicio y
#   sobrescriben validar_parametros(), calcular_costo_base() y describir().
#   -> POLIMORFISMO: es el mismo metodo, cada servicio responde distinto.
# - SOBRECARGA: Python no la tiene como tal, asi que se simula con
#   parametros opcionales (calcular_costo) y con *args (calcular_costo_total).


# ---------------------------------------------------------------
# SERVICIO (ABSTRACTA)
# ---------------------------------------------------------------
class Servicio(EntidadBase, ABC):
    IVA = 0.19

    def __init__(self, nombre, tarifa_hora, disponible=True):
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El servicio necesita un nombre.")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise ServicioInvalidoError("La tarifa por hora debe ser un numero mayor que 0.")
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)

# ----- metodos abstractos (los hijos los sobrescriben) -----
    @abstractmethod
    def validar_parametros(self):
        pass

    @abstractmethod
    def calcular_costo_base(self, horas):
        pass

    # ----- "sobrecarga" de calcular_costo -----
    # Variantes:
    #   calcular_costo(horas)                       -> solo costo base
    #   calcular_costo(horas, True)                 -> con IVA
    #   calcular_costo(horas, True, 0.10)           -> con IVA y 10% de descuento
    def calcular_costo(self, horas, con_iva=False, descuento=0.0):
        if not isinstance(horas, (int, float)) or horas <= 0:
            raise CalculoInconsistenteError("Las horas deben ser un numero mayor que 0.")
        if not 0 <= descuento < 1:
            raise CalculoInconsistenteError("El descuento debe estar entre 0 y 1 (ej: 0.10).")

        total = self.calcular_costo_base(horas)
        total -= total * descuento
        if con_iva:
            total += total * Servicio.IVA

        if total < 0:
            raise CalculoInconsistenteError("El costo calculado dio negativo.")
        return round(total, 2)

    def calcular_costo_total(self, horas, *extras):
        """Segunda forma de sobrecarga usando *args:
        extras puede traer (con_iva,) o (con_iva, descuento)."""
        if len(extras) == 0:
            return self.calcular_costo(horas)
        if len(extras) == 1:
            return self.calcular_costo(horas, extras[0])
        if len(extras) == 2:
            return self.calcular_costo(horas, extras[0], extras[1])
        raise CalculoInconsistenteError("Demasiados parametros para calcular el costo.")
