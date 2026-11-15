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

# ---------------------------------------------------------------
# SERVICIOS ESPECIALIZADOS
# ---------------------------------------------------------------
class ReservaSala(Servicio):
    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        self._capacidad = capacidad
        self.validar_parametros()

    def validar_parametros(self):
        if not isinstance(self._capacidad, int) or self._capacidad <= 0:
            raise ServicioInvalidoError("La capacidad de la sala debe ser un entero positivo.")

    def calcular_costo_base(self, horas):
        return self._tarifa_hora * horas

    def describir(self):
        return f"Sala '{self.nombre}' | capacidad {self._capacidad} personas | ${self._tarifa_hora:,.0f}/h"

 class AlquilerEquipo(Servicio):
    def __init__(self, nombre, tarifa_hora, cantidad, seguro=False, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        self._cantidad = cantidad
        self._seguro = seguro
        self.validar_parametros()

    def validar_parametros(self):
        if not isinstance(self._cantidad, int) or self._cantidad <= 0:
            raise ServicioInvalidoError("La cantidad de equipos debe ser un entero positivo.")

    def calcular_costo_base(self, horas):
        total = self._tarifa_hora * horas * self._cantidad
        if self._seguro:
            total += total * 0.05  # el seguro cuesta 5% extra
        return total

    def describir(self):
        seguro = "con seguro" if self._seguro else "sin seguro"
        return f"Equipo '{self.nombre}' x{self._cantidad} ({seguro}) | ${self._tarifa_hora:,.0f}/h c/u"

  class Asesoria(Servicio):
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, nivel, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        self._nivel = str(nivel).lower()
        self.validar_parametros()

    def validar_parametros(self):
        if self._nivel not in Asesoria.NIVELES:
            raise ServicioInvalidoError(
                f"Nivel '{self._nivel}' no valido. Use: {', '.join(Asesoria.NIVELES)}."
            )

    def calcular_costo_base(self, horas):
        return self._tarifa_hora * horas * Asesoria.NIVELES[self._nivel]

    def describir(self):
        return f"Asesoria '{self.nombre}' nivel {self._nivel} | ${self._tarifa_hora:,.0f}/h base"

# ===============================================================
# SEGMENTO 4 - Reserva, GestorFJ y simulacion de 14 operaciones
# ===============================================================
# - Reserva: une cliente + servicio + horas + estado (PENDIENTE,
#   CONFIRMADA, CANCELADA).
#   * confirmar() usa try/except/else/finally.
#   * procesar() usa ENCADENAMIENTO de excepciones (raise ... from e).
# - GestorFJ: maneja las listas internas (clientes, servicios, reservas)
#   en memoria, sin base de datos.
# - La simulacion ejecuta 14 operaciones validas e invalidas. La funcion
#   ejecutar() atrapa los errores para que el programa NUNCA se caiga y
#   todo queda registrado en el log.

# ---------------------------------------------------------------
# RESERVA
# ---------------------------------------------------------------
class Reserva(EntidadBase):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

    def __init__(self, cliente, servicio, horas):
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva necesita un cliente valido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva necesita un servicio valido.")
        if not isinstance(horas, (int, float)) or horas <= 0 or horas > 12:
            raise ReservaInvalidaError("La duracion debe estar entre 1 y 12 horas.")
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = Reserva.PENDIENTE

 @property
    def estado(self):
        return self._estado

    def confirmar(self):
        """Confirma la reserva. Usa try/except/else/finally."""
        try:
            if self._estado == Reserva.CANCELADA:
                raise OperacionNoPermitidaError("No se puede confirmar una reserva cancelada.")
            if self._estado == Reserva.CONFIRMADA:
                raise OperacionNoPermitidaError("La reserva ya estaba confirmada.")
            if not self._servicio.disponible:
                raise ServicioNoDisponibleError(f"'{self._servicio.nombre}' no esta disponible.")
        except SoftwareFJError as e:
            log.error("Fallo al confirmar reserva #%s: %s", self.id, e)
            raise
        else:
            # solo se ejecuta si NO hubo error
            self._estado = Reserva.CONFIRMADA
            log.info("Reserva #%s confirmada.", self.id)
        finally:
            # siempre se ejecuta
            log.info("Intento de confirmacion de reserva #%s finalizado.", self.id)

    def cancelar(self):
        if self._estado == Reserva.CANCELADA:
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada.")
        self._estado = Reserva.CANCELADA
        log.info("Reserva #%s cancelada.", self.id)

def procesar(self, con_iva=True, descuento=0.0):
        """Confirma y calcula el costo. Aqui se ve el ENCADENAMIENTO de excepciones."""
        try:
            self.confirmar()
            costo = self._servicio.calcular_costo(self._horas, con_iva, descuento)
        except SoftwareFJError as e:
            # raise ... from e  -> guarda la causa original
            raise ReservaInvalidaError(f"No se pudo procesar la reserva #{self.id}") from e
        return costo

    def describir(self):
        return (f"Reserva #{self.id} [{self._estado}] | {self._cliente.nombre} -> "
                f"{self._servicio.nombre} por {self._horas}h")

# ---------------------------------------------------------------
# GESTOR (encagado de manejar las listas internas)
# ---------------------------------------------------------------
class GestorFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, nombre, correo, telefono):
        cliente = Cliente(nombre, correo, telefono)
        if any(c.correo == cliente.correo for c in self.clientes):
            raise ClienteInvalidoError(f"Ya existe un cliente con el correo {cliente.correo}.")
        self.clientes.append(cliente)
        log.info("Cliente registrado: %s", cliente.describir())
        return cliente

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)
        log.info("Servicio agregado: %s", servicio.describir())
        return servicio

    def crear_reserva(self, cliente, servicio, horas):
        reserva = Reserva(cliente, servicio, horas)
        self.reservas.append(reserva)
        log.info("Reserva creada: %s", reserva.describir())
        return reserva

# ---------------------------------------------------------------
# SIMULACION (ejecucion de 14 operaciones)
# ---------------------------------------------------------------
def ejecutar(numero, titulo, funcion):
    """Ejecuta una operacion y captura cualquier error para que el programa NO se caiga."""
    print(f"\n--- Operacion {numero}: {titulo} ---")
    try:
        resultado = funcion()
    except SoftwareFJError as e:
        print(f"  [ERROR CONTROLADO] {e}")
        if e.__cause__:  # mostramos la causa si hubo encadenamiento
            print(f"    causa original: {e.__cause__}")
        log.error("Operacion %s (%s): %s | causa: %r", numero, titulo, e, e.__cause__)
    except Exception as e:  # cualquier error inesperado tambien se controla
        print(f"  [ERROR INESPERADO] {type(e).__name__}: {e}")
        log.critical("Error inesperado en operacion %s: %r", numero, e)
    else:
        print(f"  [OK] {resultado}")
        log.info("Operacion %s (%s) exitosa.", numero, titulo)
    finally:
        print("  (operacion finalizada, el sistema sigue activo)")

 def main():
    log.info("===== INICIO DE LA SIMULACION SOFTWARE FJ =====")
    g = GestorFJ()
    datos = {}  # para guardar objetos creados y usarlos en operaciones siguientes

    def op1():
        datos["ana"] = g.registrar_cliente("ana gomez", "ana@correo.com", "3001234567")
        return datos["ana"].describir()

    def op2():
        return g.registrar_cliente("Pedro", "pedro-correo.com", "3109876543")  # correo malo

    def op3():
        datos["luis"] = g.registrar_cliente("Luis Perez", "luis@mail.com", "3205551234")
        return datos["luis"].describir()

    def op4():
        return g.registrar_cliente("Maria Lopez", "luis@mail.com", "3111112222")  # correo repetido

    def op5():
        datos["sala"] = g.agregar_servicio(ReservaSala("Sala Innovacion", 50000, 12))
        return datos["sala"].describir()

    def op6():
        return g.agregar_servicio(ReservaSala("Sala Rota", -100, 8))  # tarifa negativa

    def op7():
        datos["equipo"] = g.agregar_servicio(AlquilerEquipo("Portatil Gamer", 15000, 3, seguro=True))
        datos["asesoria"] = g.agregar_servicio(Asesoria("Asesoria en Python", 40000, "senior"))
        return datos["equipo"].describir() + " / " + datos["asesoria"].describir()

    def op8():
        return g.agregar_servicio(Asesoria("Asesoria Magica", 30000, "dios"))  # nivel invalido

    def op9():
        datos["r1"] = g.crear_reserva(datos["ana"], datos["sala"], 4)
        costo = datos["r1"].procesar(con_iva=True, descuento=0.10)
        return f"{datos['r1'].describir()} | costo con IVA y 10% desc: ${costo:,.2f}"
     
    def op10():
        return g.crear_reserva(datos["luis"], datos["sala"], 30)  # 30 horas no permitido

    def op11():
        # cancelamos y luego intentamos confirmar -> operacion no permitida (encadenada)
        datos["r2"] = g.crear_reserva(datos["luis"], datos["asesoria"], 2)
        datos["r2"].cancelar()
        return datos["r2"].procesar()

    def op12():
        # servicio no disponible
        datos["equipo"].disponible = False
        r3 = g.crear_reserva(datos["ana"], datos["equipo"], 5)
        return r3.procesar()

    def op13():
        # probamos las variantes de la "sobrecarga" de costos
        a = datos["asesoria"]
        return (f"solo base: ${a.calcular_costo_total(3):,.2f} | "
                f"con IVA: ${a.calcular_costo_total(3, True):,.2f} | "
                f"IVA + 20% desc: ${a.calcular_costo_total(3, True, 0.20):,.2f}")

    def op14():
        return datos["asesoria"].calcular_costo(0)  # horas invalidas

 operaciones = [
        ("Registrar cliente valido", op1),
        ("Registrar cliente con correo invalido", op2),
        ("Registrar segundo cliente valido", op3),
        ("Registrar cliente con correo repetido", op4),
        ("Crear sala valida", op5),
        ("Crear sala con tarifa negativa", op6),
        ("Crear equipo y asesoria validos", op7),
        ("Crear asesoria con nivel invalido", op8),
        ("Reserva exitosa (con IVA y descuento)", op9),
        ("Reserva con duracion invalida", op10),
        ("Confirmar reserva cancelada", op11),
        ("Reservar servicio no disponible", op12),
        ("Probar variantes de calculo de costo", op13),
        ("Calcular costo con horas invalidas", op14),
    ]

for i, (titulo, func) in enumerate(operaciones, start=1):
        ejecutar(i, titulo, func)

    print("\n===== RESUMEN FINAL =====")
    print(f"Clientes registrados: {len(g.clientes)}")
    print(f"Servicios registrados: {len(g.servicios)}")
    print(f"Reservas creadas: {len(g.reservas)}")
    for r in g.reservas:
        print(" -", r.describir())
    print("\nRevisa el archivo 'logs_software_fj.log' para ver todos los eventos y errores.")
    log.info("===== FIN DE LA SIMULACION =====")


if __name__ == "__main__":
    main()

# Al final, el programa recorre las 14 operacions con un ciclo for, cada una protegida
# por ejecutar(), muesta un resumen de lo que quedo en las listas y registra el 
# cierre en el log. if __name__ == "__main__" hace que todo araque solo al ejecutar
# el archivo directamente.
