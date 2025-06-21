mkdir -p test_data
cd test_data

wget https://github.com/google-coral/pycoral/raw/main/test_data/parrot.jpg
wget https://github.com/google-coral/pycoral/raw/main/test_data/inat_bird_labels.txt
wget https://github.com/google-coral/pycoral/raw/main/test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite

cd ..
python3 classify_image.py \
  --model test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
  --labels test_data/inat_bird_labels.txt \
  --input test_data/parrot.jpg
