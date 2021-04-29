# Victim model ResNet34 x-vector
# For the black-box attacks we use Light ResNet34 to generate the attack and transfer them to the ResNet34
# Both models uses the same features: 80 fbanks
# Both models uses the same training data.

# # victim acoustic features
# feat_config=conf/fbank80_stmn_16k.yaml
# feat_type=fbank80_stmn

# # victim x-vector training 
# nnet_data=voxceleb2cat_train
# nnet_num_augs=6
# aug_opt="--train-aug-cfg conf/reverb_noise_aug.yml --val-aug-cfg conf/reverb_noise_aug.yml"

# batch_size_1gpu=128
# eff_batch_size=512 # effective batch size
# min_chunk=4
# max_chunk=4
# ipe=$nnet_num_augs
# lr=0.05

# nnet_type=lresnet34
# dropout=0
# embed_dim=256

# s=30
# margin_warmup=20
# margin=0.3

# nnet_opt="--resnet-type $nnet_type --in-feats 80 --in-channels 1 --in-kernel-size 3 --in-stride 1 --no-maxpool"
# opt_opt="--optim.opt-type adam --optim.lr $lr --optim.beta1 0.9 --optim.beta2 0.95 --optim.weight-decay 1e-5 --optim.amsgrad --use-amp"
# lrs_opt="--lrsched.lrsch-type exp_lr --lrsched.decay-rate 0.5 --lrsched.decay-steps 8000 --lrsched.hold-steps 40000 --lrsched.min-lr 1e-5 --lrsched.warmup-steps 1000 --lrsched.update-lr-on-opt-step"
# nnet_name=${feat_type}_${nnet_type}_e${embed_dim}_arcs${s}m${margin}_do${dropout}_adam_lr${lr}_b${eff_batch_size}_amp.v1
# nnet_num_epochs=70
# num_augs=5
# nnet_dir=exp/xvector_nnets/$nnet_name
# nnet=$nnet_dir/model_ep0070.pth

spknet_command=resnet
spknet_data=voxceleb2cat_train
spknet_config=conf/lresnet34_spknet.yaml
spknet_batch_size_1gpu=128
spknet_eff_batch_size=512 # effective batch size
spknet_dir=exp/xvector_nnets/lresnet34

