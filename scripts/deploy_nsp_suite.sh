#!/bin/bash
echo "Building ISO..."
bash build_iso.sh
echo "Installing iso.nsp..."
bash nsp_installer.sh
echo "All components ready."
