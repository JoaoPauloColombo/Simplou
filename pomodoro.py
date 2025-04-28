import flet as ft
import json
import os
from datetime import datetime
import threading
import pygame  # Para sons

# Definir o caminho do arquivo de histórico
HISTORY_FILE = "db/history.json"

# Inicializar o pygame mixer para tocar sons
pygame.mixer.init()

# Função para tocar som
def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

def load_history():
    if not os.path.exists("db"):
        os.makedirs("db")
    
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)
    
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_to_history(duration):
    history = load_history()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append({"date": now, "duration": duration})
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# Função para excluir o histórico
def delete_history(e=None):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)  # Esvaziando o conteúdo do arquivo

def main(page: ft.Page):
    page.title = "Simplou Pomodoro"
    page.window_width = 400
    page.window_height = 500
    page.theme_mode = ft.ThemeMode.LIGHT

    # Alternar entre os temas claro e escuro
    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        page.update()

    # Exibir a tela principal
    def show_home(e=None):
        page.controls.clear()
        page.add(main_view)
        page.update()

    # Exibir o histórico de ciclos com um "baralho"
    def show_history(e):
        history_data = load_history()

        # Organizando cada item do histórico com "Data" e "Duração"
        history_list = [
            ft.Column([ 
                ft.Container(
                    ft.Row([
                        ft.Column([
                            ft.Text("Data:", size=12, weight="bold"),
                            ft.Text(item['date'], size=12),
                        ], alignment=ft.MainAxisAlignment.CENTER),  # Centralizando a coluna de Data
                        ft.Column([
                            ft.Text("Duração:", size=12, weight="bold"),
                            ft.Text(item['duration'], size=12),
                        ], alignment=ft.MainAxisAlignment.CENTER)  # Centralizando a coluna de Duração
                    ], alignment=ft.MainAxisAlignment.CENTER),  # Centralizando a Row
                    width=350,
                    height=100,
                    bgcolor=ft.Colors.BLUE_GREY_200,
                    alignment=ft.alignment.center,
                    border_radius=10,
                    margin=10,
                    padding=15,
                    animate=ft.Animation(300, "ease-in-out")
                )
            ]) for item in history_data
        ] or [ft.Text("Nenhum histórico disponível.")]

        page.controls.clear()
        page.add(
            ft.Column([ 
                ft.Row([ft.Text("Histórico", size=30, weight="bold"),
                        ft.IconButton(icon=ft.Icons.BRIGHTNESS_6, on_click=toggle_theme)],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Column(history_list, scroll=ft.ScrollMode.AUTO, expand=True, alignment=ft.MainAxisAlignment.CENTER),  # Centralizando a coluna de histórico
                ft.Row([
                    ft.ElevatedButton("Excluir Histórico", on_click=delete_history,width=150, height=50, bgcolor=ft.Colors.RED, color="white"),
                    ft.ElevatedButton("Voltar", on_click=show_home, width=150, height=50, bgcolor=ft.Colors.BLUE, color="white")
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], expand=True, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)  # Centralizando a tela
        )
        page.update()

    duration = 25 * 60  # 25 minutos
    time_left = ft.Text(value="25:00", size=40, weight="bold")
    status_text = ft.Text(value="", size=14, italic=True)
    running = False
    custom_minutes = ft.TextField(label="Minutos", width=200, keyboard_type=ft.KeyboardType.NUMBER)

    # Formatar o tempo
    def format_time(seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    # Atualizar o tempo no temporizador
    def update_time():
        nonlocal duration, running
        if running:
            if duration > 0:
                duration -= 1
                time_left.value = format_time(duration)
                page.update()
            else:
                finish_cycle()

    # Iniciar o temporizador
    def start_timer(e):
        nonlocal running
        if not running:
            running = True
            status_text.value = "Foco iniciado!"
            play_sound("sound.mp3")  # Som ao iniciar
            page.update()

            def timer():
                if running:
                    update_time()
                    threading.Timer(1, timer).start()

            timer()

    # Pausar o temporizador
    def pause_timer(e):
        nonlocal running
        running = False
        status_text.value = "Temporizador pausado."
        play_sound("sound.mp3")  # Som ao pausar
        page.update()

    # Resetar o temporizador
    def reset_timer(e):
        nonlocal running, duration
        running = False
        duration = 25 * 60
        time_left.value = format_time(duration)
        status_text.value = "Temporizador reiniciado."
        play_sound("sound.mp3")  # Som ao resetar
        page.update()

    # Finalizar o ciclo e salvar o histórico
    def finish_cycle(e=None):
        nonlocal running, duration
        running = False
        status_text.value = "Tempo finalizado."
        save_to_history(format_time(duration))
        duration = 25 * 60
        time_left.value = format_time(duration)
        play_sound("sound.mp3")  # Som ao finalizar o ciclo
        page.update()

    # Função para configurar o tempo
    def set_custom_time(e):
        nonlocal duration
        try:
            minutes = int(custom_minutes.value)
            if minutes <= 0:
                raise ValueError
            duration = minutes * 60
            time_left.value = format_time(duration)
            status_text.value = f"Pomodoro definido para {minutes} minutos."
            show_home()
        except ValueError:
            status_text.value = "Por favor, insira um número válido maior que zero."
        page.update()

    # Definir tempos pré-definidos
    def set_timer(duration_minutes):
        nonlocal duration
        duration = duration_minutes * 60
        time_left.value = format_time(duration)
        status_text.value = f"Pomodoro definido para {duration_minutes} minutos."
        page.update()

    # Exibir a tela para configurar o tempo
    def show_set_timer_page(e):
        page.controls.clear()
        page.add(
            ft.Column([ 
                ft.Row([ft.Text("Definir Tempo do Pomodoro", size=25, weight="bold")],
                       alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Text("Tempo personalizado:", size=16, weight="bold"),
                    margin=ft.margin.only(top=20)
                ),
                custom_minutes,
                ft.Row([ 
                    ft.ElevatedButton("Salvar", on_click=set_custom_time),
                ], alignment=ft.MainAxisAlignment.CENTER),
                # Botões para tempos predefinidos com texto em cima de cada botão
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Padrão para foco", size=14, weight="bold"),
                                    ft.ElevatedButton("25 Min", on_click=lambda e: set_timer(25)),
                                ], 
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            margin=ft.margin.only(top=10)
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Sessões de estudo e trabalho", size=14, weight="bold"),
                                    ft.ElevatedButton("50 Min", on_click=lambda e: set_timer(50)),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            margin=ft.margin.only(top=10)
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Pausas mais curtas", size=14, weight="bold"),
                                    ft.ElevatedButton("15 Min", on_click=lambda e: set_timer(15)),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            margin=ft.margin.only(top=10)
                        ),
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                status_text,
                ft.ElevatedButton("Voltar", on_click=show_home, width=150, height=50, bgcolor=ft.Colors.BLUE, color="white")
            ], 
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True)
        )
        page.update()

    # Definir a interface principal
    main_view = ft.Column(
        [
            ft.Row([ft.Text("Simplou Pomodoro", size=30, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([ft.IconButton(icon=ft.Icons.BRIGHTNESS_6, on_click=toggle_theme),
                    ft.IconButton(icon=ft.Icons.HISTORY, on_click=show_history)],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(content=time_left, alignment=ft.alignment.center, margin=20),
            ft.Row([ 
                ft.ElevatedButton("Iniciar", on_click=start_timer),
                ft.ElevatedButton("Pausar", on_click=pause_timer),
                ft.ElevatedButton("Resetar", on_click=reset_timer),
                ft.ElevatedButton("Configurar Tempo", on_click=show_set_timer_page,),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.ElevatedButton("Finalizar ciclo",width=150, height=50, on_click=finish_cycle, bgcolor=ft.Colors.RED, color="white"),
            status_text
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )

    page.add(main_view)

if __name__ == "__main__":
    ft.app(target=main)
    