all: install

install:
	cp m1.py /usr/local/bin/m1
	cp Examples/tmux_menu.py /home/stcarolas/.config/m1/generators
	cp Examples/menu /home/stcarolas/.config/m1/
	

install_to_home:
	cp m1.py ~/.local/bin/m1
	cp Examples/tmux_menu.py /home/stcarolas/.config/m1/generators
	cp Examples/menu ~/.config/m1/
