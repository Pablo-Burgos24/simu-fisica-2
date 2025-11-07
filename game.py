import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Constantes Físicas ---
C_AGUA = 4186  # Capacidad calorífica específica del agua (J/kg°C)
RHO_AGUA = 1.0   # Densidad del agua (kg/L)

class KettleSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Termodinámico de Pava Eléctrica")
        self.root.geometry("1000x650")

        # --- Frames ---
        controls_frame = ttk.LabelFrame(root, text="Parámetros de Simulación")
        controls_frame.pack(pady=10, padx=10, fill="x")

        graph_frame = ttk.Frame(root)
        graph_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Variables de Control (StringVars) ---
        self.power_var = tk.StringVar()
        self.volume_var = tk.StringVar()
        self.t_initial_var = tk.StringVar()
        self.t_final_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.efficiency_var = tk.StringVar(value="90.0")  # Default 90%

        # --- Creación de Entradas (Inputs) ---
        self.create_entry(controls_frame, "Potencia (P) [Watts]:", self.power_var, 0)
        self.create_entry(controls_frame, "Volumen de Agua (V) [Litros]:", self.volume_var, 1)
        self.create_entry(controls_frame, "Temp. Inicial (Ti) [°C]:", self.t_initial_var, 2)
        self.create_entry(controls_frame, "Temp. Final (Tf) [°C]:", self.t_final_var, 3)
        self.create_entry(controls_frame, "Tiempo (t) [segundos]:", self.time_var, 4)
        self.create_entry(controls_frame, "Eficiencia (η) [%]:", self.efficiency_var, 5)

        # --- Botones ---
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.grid(row=0, column=2, rowspan=2, padx=20)
        
        calc_button = ttk.Button(btn_frame, text="Calcular y Graficar", command=self.calculate_and_plot)
        calc_button.pack(pady=5, fill="x")
        
        reset_button = ttk.Button(btn_frame, text="Resetear", command=self.reset)
        reset_button.pack(pady=5, fill="x")

        # --- Setup del Gráfico Matplotlib ---
        self.fig, self.ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.ax.set_title("Evolución de la Temperatura")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Temperatura (°C)")
        self.ax.grid(True)

    def create_entry(self, frame, text, variable, row):
        """Helper para crear un Label y un Entry"""
        label = ttk.Label(frame, text=text)
        label.grid(row=row, column=0, padx=5, pady=8, sticky="w")
        entry = ttk.Entry(frame, textvariable=variable, width=15)
        entry.grid(row=row, column=1, padx=5, pady=8)

    def get_float(self, var):
        """Convierte un StringVar a float, o None si está vacío/es inválido"""
        try:
            return float(var.get())
        except ValueError:
            return None

    def calculate_and_plot(self):
        """Función principal: calcula el valor faltante y actualiza el gráfico"""
        try:
            # 1. Obtener todos los valores
            params = {
                'P': self.get_float(self.power_var),
                'V': self.get_float(self.volume_var),
                'Ti': self.get_float(self.t_initial_var),
                'Tf': self.get_float(self.t_final_var),
                't': self.get_float(self.time_var),
                'eta': self.get_float(self.efficiency_var)
            }

            # 2. Identificar el valor faltante
            missing_var = None
            missing_count = 0
            for key, value in params.items():
                if value is None:
                    missing_var = key
                    missing_count += 1
            
            # 3. Validar entradas
            if missing_count > 1:
                messagebox.showerror("Error", "Por favor, deja solo UN campo vacío para calcular.")
                return
            if missing_count == 0:
                # Todos los campos están llenos, solo graficamos
                pass
            if params['eta'] is None:
                messagebox.showerror("Error", "La Eficiencia no puede estar vacía.")
                return

            # Convertir eficiencia a decimal y volumen a masa
            eta = params['eta'] / 100.0
            
            # 4. Calcular el valor faltante
            if missing_var:
                m = params['V'] * RHO_AGUA if missing_var != 'V' else None
                delta_T = params['Tf'] - params['Ti'] if (missing_var != 'Tf' and missing_var != 'Ti') else None
                Q = m * C_AGUA * delta_T if (m is not None and delta_T is not None) else None
                
                if missing_var == 'P':
                    # P = (m * c * (Tf - Ti)) / (t * eta)
                    P_calc = Q / (params['t'] * eta)
                    self.power_var.set(f"{P_calc:.2f}")
                    params['P'] = P_calc
                
                elif missing_var == 't':
                    # t = (m * c * (Tf - Ti)) / (P * eta)
                    t_calc = Q / (params['P'] * eta)
                    self.time_var.set(f"{t_calc:.2f}")
                    params['t'] = t_calc

                elif missing_var == 'V':
                    # m = (P * t * eta) / (c * (Tf - Ti)) -> V = m / rho
                    m_calc = (params['P'] * params['t'] * eta) / (C_AGUA * delta_T)
                    V_calc = m_calc / RHO_AGUA
                    self.volume_var.set(f"{V_calc:.3f}")
                    params['V'] = V_calc

                elif missing_var == 'Tf':
                    # Tf = Ti + (P * t * eta) / (m * c)
                    Tf_calc = params['Ti'] + (params['P'] * params['t'] * eta) / (m * C_AGUA)
                    self.t_final_var.set(f"{Tf_calc:.2f}")
                    params['Tf'] = Tf_calc

                elif missing_var == 'Ti':
                    # Ti = Tf - (P * t * eta) / (m * c)
                    Ti_calc = params['Tf'] - (params['P'] * params['t'] * eta) / (m * C_AGUA)
                    self.t_initial_var.set(f"{Ti_calc:.2f}")
                    params['Ti'] = Ti_calc

            # 5. Graficar los resultados
            self.plot_graph(params)

        except Exception as e:
            messagebox.showerror("Error de Cálculo", f"Ocurrió un error: {e}\n"
                                 "Asegúrate de que todos los valores (excepto el que se va a calcular) sean números válidos.")
    def reset(self):
        """Limpia todos los campos de entrada y el gráfico"""
        self.power_var.set("")
        self.volume_var.set("")
        self.t_initial_var.set("")
        self.t_final_var.set("")
        self.time_var.set("")
        self.efficiency_var.set("90.0") # Vuelve al default
        
        self.ax.clear()
        self.ax.set_title("Evolución de la Temperatura")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Temperatura (°C)")
        self.ax.grid(True)
        self.canvas.draw()
        
    def plot_graph(self, params):
        """Actualiza el canvas de Matplotlib con la simulación"""
        
        # Obtener valores finales (ahora todos deberían estar llenos)
        P = params['P']
        V = params['V']
        Ti = params['Ti']
        Tf = params['Tf']
        eta = params['eta'] / 100.0
        
        # Validar que tengamos todo lo necesario para graficar
        if any(v is None for v in [P, V, Ti, Tf, eta]):
            messagebox.showinfo("Info", "Se necesitan todos los valores para graficar la curva.")
            return

        m = V * RHO_AGUA
        
        # Calcular el tiempo final total basado en los parámetros
        # t = (m * c * (Tf - Ti)) / (P * eta)
        t_final_calculado = (m * C_AGUA * (Tf - Ti)) / (P * eta)

        if t_final_calculado <= 0:
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'Datos inválidos (p.ej. Temp. Final <= Temp. Inicial)', 
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, color='red')
            self.canvas.draw()
            return

        # Crear los arrays para el gráfico
        t_array = np.linspace(0, t_final_calculado, 100)
        
        # Ecuación de T en función del tiempo: T(t) = Ti + (P * eta / (m * c)) * t
        temp_array = Ti + (P * eta / (m * C_AGUA)) * t_array

        # Actualizar el gráfico
        self.ax.clear()
        self.ax.plot(t_array, temp_array, lw=2, color='red')
        self.ax.set_title("Evolución de la Temperatura de la Pava")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Temperatura (°C)")
        self.ax.set_ylim(bottom=Ti - (Tf-Ti)*0.1, top=Tf + (Tf-Ti)*0.1) # Margen visual
        self.ax.set_xlim(0, t_final_calculado)
        self.ax.grid(True)
        self.ax.axhline(Tf, color='gray', linestyle='--', label=f'Temp. Final ({Tf}°C)')
        self.ax.axhline(Ti, color='blue', linestyle='--', label=f'Temp. Inicial ({Ti}°C)')
        self.ax.legend()
        
        self.canvas.draw()

# --- Bloque Principal para ejecutar la App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = KettleSimulator(root)
    root.mainloop()