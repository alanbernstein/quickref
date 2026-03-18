#INSTALL_DIR="$HOME/code/py/quickref"
#COMMAND_DIR="$(HOME)/cmd"
#COMMAND_NAME="qr"

export QR_COMMAND_DIR   ?= "$(HOME)/cmd"
export QR_COMMAND_NAME  ?= "qr"
export QR_DATA_DIR      ?= "$(HOME)/qr"
export QR_APP_FILENAME  ?= qr.html

#include default.env

QR_INSTALL_DIR   ?= "$(shell pwd)"

render:
	echo $(QR_DATA_DIR)
	echo $(QR_APP_FILENAME)
	python3 render.py

install-zsh:
	echo $(QR_COMMAND_DIR)
	echo $(QR_COMMAND_NAME)
	echo $(QR_DATA_DIR)

	@mkdir -p "$(QR_COMMAND_DIR)"
	@cd "$(QR_COMMAND_DIR)"
	@echo 'PATH="$(PATH):$(QR_COMMAND_DIR)" >> $(HOME)/.zshrc'
	@echo 'QR=$(QR_DATA_DIR) >> $(HOME)/.zshrc'
	@ln -s "$(QR_INSTALL_DIR)/quickref.py" "$(QR_COMMAND_NAME)"