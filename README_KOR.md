### Data
- http://www.aihub.or.kr/aidata/87

### 전처리
```
python ./preprocess_ko_mt/data_merge_and_convert.py

mkdir -p ./data/mono/en/ && mkdir -p ./data/mono/ko

cp ./preprocess_ko_mt/data/merged/all.en ./data/mono/en/
cp ./preprocess_ko_mt/data/merged/all.ko ./data/mono/ko/

# 1,602,418 wc -l ./data/mono/ko/all.ko
# 1,602,418 wc -l ./data/mono/en/all.en

## RE
rm ./data/mono/ko/all.ko.tok && rm ./data/mono/en/all.en.tok
rm -rf ./data/processed/en-ko/*

./ko-get-data-nmt.sh --src en --tgt ko

# 1,602,418 wc -l ./data/mono/ko/all.ko.tok
# 1,602,418 wc -l ./data/mono/en/all.en.tok
# 1,602,418 wc -l ./data/processed/en-ko/train.ko
# 1,602,418 wc -l ./data/processed/en-ko/train.en


## Total Data
mv ./data/processed/en-ko/train.ko ./data/processed/en-ko/tot.ko
mv ./data/processed/en-ko/train.en ./data/processed/en-ko/tot.en

## Test Data (3000)
tail -n 3000 ./data/processed/en-ko/tot.ko > ./data/processed/en-ko/test.en-ko.ko
tail -n 3000 ./data/processed/en-ko/tot.en > ./data/processed/en-ko/test.en-ko.en
head -n -3000 ./data/processed/en-ko/tot.ko > ./data/processed/en-ko/train_val.ko
head -n -3000 ./data/processed/en-ko/tot.en > ./data/processed/en-ko/train_val.en

# 1,599,418 wc -l ./data/processed/en-ko/train_val.ko
# 1,599,418 wc -l ./data/processed/en-ko/train_val.en

## Validation Data (3000)
tail -n 3000 ./data/processed/en-ko/train_val.ko > ./data/processed/en-ko/valid.en-ko.ko
tail -n 3000 ./data/processed/en-ko/train_val.en > ./data/processed/en-ko/valid.en-ko.en
head -n -3000 ./data/processed/en-ko/train_val.ko > ./data/processed/en-ko/train.ko
head -n -3000 ./data/processed/en-ko/train_val.en > ./data/processed/en-ko/train.en

## Train Data
# 1,596,418 wc -l ./data/processed/en-ko/train.ko
# 1,596,418 wc -l ./data/processed/en-ko/train.en

## 전처리 후 데이터
rm ./data/processed/en-ko/*.pth

## Binarize
./ko-get-data-nmt.sh --src en --tgt ko

## 확인
ls -lha ./data/processed/en-ko/
```

### 학습
(1) LM
```
MASTER_PORT=15001

python \
    train.py \
    --master_port=$MASTER_PORT \
    --exp_name enko_mlm_v0.5.0 \
    --dump_path ./dumped \
    --data_path ./data/processed/en-ko/ \
    --lgs 'en-ko' \
    --clm_steps '' \
    --mlm_steps 'en,ko' \
    --emb_dim 1024 \
    --n_layers 6 \
    --n_heads 8 \
    --dropout 0.1 \
    --attention_dropout 0.1 \
    --gelu_activation true \
    --batch_size 64 \
    --bptt 256 \
    --optimizer adam,lr=0.0001 \
    --epoch_size 200000 \
    --validation_metrics _valid_mlm_ppl \
    --stopping_criterion _valid_mlm_ppl,10 \
    --fp16 true \
    --amp 1
```

(2) MT
```
XXX=<PID>

python -u \
    train.py \
    --master_port=$MASTER_PORT \
    --exp_name unsupMT_enko_v0.5.0 \
    --dump_path ./dumped \
    --reload_model 'dumped/unsupMT_enko_v0.5.0/XXX/best-valid_mlm_ppl.pth,dumpedunsupMT_enko_v0.5.0/XXX/best-valid_mlm_ppl.pth' \
    --data_path ./data/processed/en-ko/ \
    --lgs 'en-ko' \
    --ae_steps 'en,ko' \
    --bt_steps 'en-ko-en,ko-en-ko'  \
    --word_shuffle 3 \
    --word_dropout 0.1 \
    --word_blank 0.1 \
    --lambda_ae '0:1,100000:0.1,300000:0' \
    --encoder_only false  \
    --emb_dim 1024  \
    --n_layers 6 \
    --n_heads 8 \
    --dropout 0.1 \
    --attention_dropout 0.1 \
    --gelu_activation true \
    --tokens_per_batch 2000 \
    --batch_size 32 \
    --bptt 256 \
    --optimizer adam_inverse_sqrt,beta1=0.9,beta2=0.98,lr=0.0001 \
    --epoch_size 200000 \
    --eval_bleu true \
    --stopping_criterion 'valid_en-ko_mt_bleu,10' \
    --validation_metrics 'valid_en-ko_mt_bleu' \
    --fp16 true \
    --amp 1
```

## 테스트
```
# head -n 30 ./data/processed/en-ko/test.en-ko.ko > test_input.txt
# sed -i 's/@@ //g' test_input.txt
or
echo '서버가 일시적으로 사용할 수 없거나 사용자가 너무 많은 상태일 수 있습니다. ' > test_input.txt

tools/fastBPE/fast applybpe test_input_bpe.txt test_input.txt ./data/processed/en-ko/codes
cat test_input_bpe.txt | python translate.py --dump_path=./dumped/ --exp_name=unsupMT_enko_v0.5.0 --exp_id=XXX --model_path=./dumped/unsupMT_enko_v0.5.0/XXX/best-valid_en-ko_mt_bleu.pth --output_path output --src_lang ko --tgt_lang en
cat output | python translate.py --dump_path=./dumped/ --exp_name=unsupMT_enko_v0.5.0 --exp_id=XXX --model_path=./dumped/unsupMT_enko_v0.5.0/XXX/best-valid_en-ko_mt_bleu.pth --output_path rev_output --src_lang en --tgt_lang ko
sed -i 's/@@ //g' rev_output
```

## 결과

```
head -n 3 test_input.txt
# 서버가 일시적으로 사용할 수 없거나 사용자가 너무 많은 상태일 수 있습니다.
```

```
head -n 3 output
# If the server cannot be used temporarily or there can be too many users .
```

```
head -n 3 rev_output
# 서버를 일시적으로 사용할 수 없거나 사용자가 너무 많을 수 있습니다 .
```