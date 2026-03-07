# -*- coding: utf-8 -*-
# =============================================================================
# Simulación de Procesos en un Sistema Operativo de Tiempo Compartido
# Usando SimPy (Discrete Event Simulation)
# =============================================================================
# Universidad del Valle de Guatemala
# Programación - Semestre 3
# =============================================================================

import simpy
import random
import statistics
import matplotlib
import os

# Configurar backend grafico compatible con cualquier sistema operativo
try:
    matplotlib.use('TkAgg')
except Exception:
    pass  # Usa el backend por defecto si TkAgg no esta disponible

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Semilla para reproducibilidad
# ---------------------------------------------------------------------------
RANDOM_SEED = 42


# ---------------------------------------------------------------------------
# Función del proceso (ciclo de vida)
# ---------------------------------------------------------------------------
def proceso(env, nombre, ram, cpu, memoria_necesaria, instrucciones, cpu_speed, tiempos):
    """
    Simula el ciclo de vida de un proceso en el sistema operativo.
    new -> ready -> running -> (terminated / waiting / ready)
    """
    llegada = env.now  # Tiempo de llegada al sistema

    # ---- NEW: solicitar memoria RAM ----
    yield ram.get(memoria_necesaria)

    # ---- READY: esperar por el CPU ----
    while instrucciones > 0:
        with cpu.request() as req:
            yield req  # Esperar turno en la cola del CPU

            # ---- RUNNING: ejecutar instrucciones ----
            ejecutar = min(instrucciones, cpu_speed)
            yield env.timeout(1)  # 1 unidad de tiempo en el CPU
            instrucciones -= ejecutar

        # Al salir del CPU, determinar siguiente estado
        if instrucciones <= 0:
            # ---- TERMINATED ----
            break
        else:
            decision = random.randint(1, 21)
            if decision == 1:
                # ---- WAITING: operaciones de I/O ----
                yield env.timeout(1)  # Tiempo de I/O
                # Regresa a ready (vuelve al while)
            # Si decision == 2 o cualquier otro, regresa a ready directamente

    # Devolver memoria al salir
    ram.put(memoria_necesaria)

    # Registrar tiempo total en el sistema
    tiempo_total = env.now - llegada
    tiempos.append(tiempo_total)


# ---------------------------------------------------------------------------
# Generador de llegadas de procesos
# ---------------------------------------------------------------------------
def generador_procesos(env, ram, cpu, num_procesos, intervalo, cpu_speed, tiempos):
    """
    Genera procesos con llegadas siguiendo una distribución exponencial.
    """
    for i in range(num_procesos):
        memoria_necesaria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)

        env.process(
            proceso(env, f"Proceso {i}", ram, cpu, memoria_necesaria,
                    instrucciones, cpu_speed, tiempos)
        )

        # Tiempo entre llegadas (distribución exponencial)
        t_llegada = random.expovariate(1.0 / intervalo)
        yield env.timeout(t_llegada)


# ---------------------------------------------------------------------------
# Función principal de simulación
# ---------------------------------------------------------------------------
def correr_simulacion(num_procesos, intervalo, ram_capacity, cpu_speed, num_cpus):
    """
    Ejecuta una simulación con los parámetros dados y retorna
    el promedio y la desviación estándar del tiempo de los procesos.
    """
    random.seed(RANDOM_SEED)

    env = simpy.Environment()
    ram = simpy.Container(env, init=ram_capacity, capacity=ram_capacity)
    cpu = simpy.Resource(env, capacity=num_cpus)

    tiempos = []

    env.process(
        generador_procesos(env, ram, cpu, num_procesos, intervalo, cpu_speed, tiempos)
    )
    env.run()

    promedio = statistics.mean(tiempos)
    desviacion = statistics.stdev(tiempos) if len(tiempos) > 1 else 0.0

    return promedio, desviacion


# ---------------------------------------------------------------------------
# Configuración de escenarios
# ---------------------------------------------------------------------------
CANTIDADES_PROCESOS = [25, 50, 100, 150, 200]
INTERVALOS = [10, 5, 1]

ESCENARIOS = {
    "Base (RAM=100, CPU_speed=3, 1 CPU)": {
        "ram": 100, "cpu_speed": 3, "num_cpus": 1
    },
    "RAM=200": {
        "ram": 200, "cpu_speed": 3, "num_cpus": 1
    },
    "CPU rápido (speed=6)": {
        "ram": 100, "cpu_speed": 6, "num_cpus": 1
    },
    "2 CPUs": {
        "ram": 100, "cpu_speed": 3, "num_cpus": 2
    },
}


# ---------------------------------------------------------------------------
# Función para generar una gráfica comparativa
# ---------------------------------------------------------------------------
def generar_grafica(resultados, titulo, nombre_archivo, carpeta):
    """
    Genera una gráfica de líneas donde cada línea representa un intervalo.
    Eje X: número de procesos, Eje Y: tiempo promedio.
    """
    plt.figure(figsize=(10, 6))

    colores = {10: '#2196F3', 5: '#FF9800', 1: '#F44336'}
    marcadores = {10: 'o', 5: 's', 1: '^'}

    for intervalo in INTERVALOS:
        promedios = [resultados[(n, intervalo)][0] for n in CANTIDADES_PROCESOS]
        plt.plot(
            CANTIDADES_PROCESOS, promedios,
            marker=marcadores[intervalo],
            color=colores[intervalo],
            linewidth=2,
            markersize=8,
            label=f"Intervalo = {intervalo}"
        )

    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel("Número de procesos", fontsize=12)
    plt.ylabel("Tiempo promedio", fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    ruta = os.path.join(carpeta, nombre_archivo)
    plt.savefig(ruta, dpi=150)
    print(f"   Grafica guardada: {nombre_archivo}")
    plt.show(block=False)
    plt.pause(0.5)


# ---------------------------------------------------------------------------
# Función para generar gráfica comparativa de estrategias
# ---------------------------------------------------------------------------
def generar_grafica_comparativa(todos_resultados, intervalo, carpeta):
    """
    Para un intervalo dado, compara todas las estrategias en una sola gráfica.
    """
    plt.figure(figsize=(12, 7))

    colores_esc = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
    marcadores_esc = ['o', 's', '^', 'D']

    for idx, (nombre_esc, resultados) in enumerate(todos_resultados.items()):
        promedios = [resultados[(n, intervalo)][0] for n in CANTIDADES_PROCESOS]
        plt.plot(
            CANTIDADES_PROCESOS, promedios,
            marker=marcadores_esc[idx],
            color=colores_esc[idx],
            linewidth=2,
            markersize=8,
            label=nombre_esc
        )

    plt.title(f"Comparación de estrategias (Intervalo = {intervalo})",
              fontsize=14, fontweight='bold')
    plt.xlabel("Número de procesos", fontsize=12)
    plt.ylabel("Tiempo promedio", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    nombre = f"comparacion_intervalo_{intervalo}.png"
    ruta = os.path.join(carpeta, nombre)
    plt.savefig(ruta, dpi=150)
    print(f"   Grafica comparativa guardada: {nombre}")
    plt.show(block=False)
    plt.pause(0.5)


# ===========================================================================
# MAIN
# ===========================================================================
if __name__ == "__main__":

    # Carpeta para guardar las gráficas
    carpeta_graficas = os.path.dirname(os.path.abspath(__file__))

    print("=" * 70)
    print("  SIMULACION DE PROCESOS - SISTEMA OPERATIVO DE TIEMPO COMPARTIDO")
    print("=" * 70)

    todos_resultados = {}

    for nombre_escenario, params in ESCENARIOS.items():
        print(f"\n{'-' * 70}")
        print(f"  ESCENARIO: {nombre_escenario}")
        print(f"  RAM={params['ram']}, CPU_speed={params['cpu_speed']}, "
              f"CPUs={params['num_cpus']}")
        print(f"{'-' * 70}")

        resultados = {}

        for intervalo in INTERVALOS:
            print(f"\n  Intervalo de llegada: {intervalo}")
            print(f"  {'Procesos':<12} {'Promedio':<15} {'Desv. Estandar':<15}")
            print(f"  {'-' * 42}")

            for n in CANTIDADES_PROCESOS:
                promedio, desviacion = correr_simulacion(
                    num_procesos=n,
                    intervalo=intervalo,
                    ram_capacity=params["ram"],
                    cpu_speed=params["cpu_speed"],
                    num_cpus=params["num_cpus"]
                )
                resultados[(n, intervalo)] = (promedio, desviacion)
                print(f"  {n:<12} {promedio:<15.4f} {desviacion:<15.4f}")

        todos_resultados[nombre_escenario] = resultados

        # Generar gráfica individual del escenario
        nombre_archivo = nombre_escenario.replace(" ", "_").replace("(", "").replace(")", "")
        nombre_archivo = nombre_archivo.replace(",", "").replace("=", "").replace("/", "_")
        nombre_archivo = f"grafica_{nombre_archivo}.png"
        generar_grafica(resultados, nombre_escenario, nombre_archivo, carpeta_graficas)

    # -----------------------------------------------------------------------
    # Gráficas comparativas por intervalo
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("  GRÁFICAS COMPARATIVAS DE ESTRATEGIAS")
    print(f"{'=' * 70}")

    for intervalo in INTERVALOS:
        generar_grafica_comparativa(todos_resultados, intervalo, carpeta_graficas)

    # -----------------------------------------------------------------------
    # Análisis y conclusión
    # -----------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("  ANÁLISIS Y CONCLUSIÓN")
    print(f"{'=' * 70}")

    # Calcular el promedio global de cada estrategia (sobre todos los escenarios)
    print(f"\n  {'Estrategia':<45} {'Promedio Global':<15}")
    print(f"  {'-' * 60}")

    mejor_estrategia = None
    mejor_promedio = float('inf')

    for nombre_esc, resultados in todos_resultados.items():
        todos_tiempos = [resultados[(n, i)][0]
                         for n in CANTIDADES_PROCESOS for i in INTERVALOS]
        promedio_global = statistics.mean(todos_tiempos)
        print(f"  {nombre_esc:<45} {promedio_global:<15.4f}")

        if promedio_global < mejor_promedio:
            mejor_promedio = promedio_global
            mejor_estrategia = nombre_esc

    print(f"\n  * MEJOR ESTRATEGIA: {mejor_estrategia}")
    print(f"    Promedio global mas bajo: {mejor_promedio:.4f}")
    print()
    print("  JUSTIFICACION:")
    print("  La estrategia seleccionada logra el menor tiempo promedio global")
    print("  de ejecucion de procesos considerando todas las combinaciones de")
    print("  intervalos de llegada y cantidades de procesos. Al comparar las")
    print("  cuatro configuraciones:")
    print("  - Incrementar RAM a 200 reduce la espera por memoria.")
    print("  - Un CPU mas rapido (6 instrucciones/ciclo) reduce ciclos en el CPU.")
    print("  - Dos CPUs permiten atender procesos en paralelo.")
    print("  La estrategia ganadora ofrece la mayor reduccion en el cuello de")
    print("  botella principal del sistema.")
    print(f"\n{'=' * 70}")

    # Mantener todas las ventanas de graficas abiertas
    print("\n  Cierre las ventanas de graficas para finalizar el programa.")
    plt.show()
