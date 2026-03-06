Correr: Simulacion.py

Pablo Orantes #25563
Se implementó una simulación de procesos en un sistema operativo de tiempo compartido utilizando la librería SimPy. El programa simula el ciclo de vida de procesos que llegan al sistema, solicitan memoria RAM, compiten por el CPU y pueden realizar operaciones de I/O. Se evaluaron diferentes configuraciones del sistema (cantidad de RAM, velocidad del CPU y número de CPUs) y se generaron gráficas comparativas para analizar el rendimiento.

Resultados
Se ejecutaron simulaciones para diferentes cantidades de procesos (25, 50, 100, 150, 200) y tres intervalos de llegada (10, 5 y 1 unidad de tiempo). Los resultados se analizaron en cuatro escenarios:

Base (RAM=100, CPU_speed=3, 1 CPU)
RAM=200
CPU rápido (speed=6)
2 CPUs
Análisis de Estrategias
Se calculó el promedio global de tiempo de ejecución para cada estrategia (combinando todos los escenarios) y se identificó la mejor configuración:

Mejor Estrategia: RAM=200
Promedio Global: 16.5476
Justificación
La estrategia con RAM=200 logró el menor tiempo promedio global de ejecución. Al incrementar la memoria disponible, se reduce la espera de los procesos por recursos de memoria, permitiendo que más procesos se ejecuten concurrently o con menos bloqueos. Esto demuestra que, en este escenario de simulación, la disponibilidad de memoria es un factor más limitante que la velocidad del CPU o la cantidad de CPUs.

Gráficas Generadas
Se generaron gráficas comparativas para cada escenario, mostrando la evolución del tiempo promedio de ejecución en función del número de procesos. Las gráficas muestran cómo el tiempo de ejecución aumenta con la carga del sistema, pero la estrategia con mayor RAM mantiene un rendimiento superior en general.

Configuración del Sistema
Cantidad de Procesos: 25, 50, 100, 150, 200
Intervalo de Llegada: 10, 5, 1
RAM: 100 o 200 unidades
CPU Speed: 3 o 6 instrucciones/ciclo
Número de CPUs: 1 o 2


Git: https://github.com/PJOS17/Simulaci-n-de-Procesos-con-Simpy
