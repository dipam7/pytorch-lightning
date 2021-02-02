# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import torch

from pytorch_lightning.utilities.apply_func import apply_to_collection


class PredictLoop(object):
    def __init__(self, trainer):
        self.trainer = trainer
        self.max_batches = None
        self.num_dataloaders = None

    def on_trainer_init(self):
        self.trainer.num_val_batches = []
        self.trainer.num_sanity_val_batches = []
        self.trainer.num_test_batches = []
        self.trainer.test_dataloaders = None
        self.trainer.val_dataloaders = None
        self.trainer.running_sanity_check = False

        # when .test() is called, it sets this
        self.trainer.tested_ckpt_path = None

        # when true, prints test results
        self.trainer.verbose_test = True

    def get_predict_dataloaders(self, max_batches):
        # select dataloaders
        model = self.trainer.get_model()
        self.trainer.reset_predict_dataloader(model)
        dataloaders = self.trainer.predict_dataloaders
        new_max_batches = self.trainer.num_predict_batches

        if max_batches is None:
            max_batches = new_max_batches

        return dataloaders, max_batches

    def should_skip_predict(self, dataloaders, max_batches):
        # skip when dataloaders aren't defined
        if dataloaders is None:
            return True

        # enable disabling validation step with limit_val_batches = 0
        should_skip = sum(max_batches) == 0
        if should_skip:
            return True

        return False

    def on_predict_model_eval(self, *_, **__):
        model_ref = self.trainer.get_model()
        model_ref.on_predict_model_eval()

<<<<<<< HEAD
=======
    def on_evaluation_model_train(self, *_, **__):
        model_ref = self.trainer.get_model()
        if self.testing:
            model_ref.on_test_model_train()
        else:
            model_ref.on_validation_model_train()

    def on_evaluation_end(self, *args, **kwargs):
        if self.testing:
            self.trainer.call_hook('on_test_end', *args, **kwargs)
        else:
            self.trainer.call_hook('on_validation_end', *args, **kwargs)

    def reload_evaluation_dataloaders(self):
        model = self.trainer.get_model()
        if self.testing:
            self.trainer.reset_test_dataloader(model)
        else:
            self.trainer.reset_val_dataloader(model)

>>>>>>> a97afb4b (add predict_loop)
    def setup(self, model, max_batches, dataloaders):
        # copy properties for forward overrides
        self.trainer.model_connector.copy_trainer_model_properties(model)

        # convert max_batches to list
        if isinstance(max_batches, int):
            max_batches = [max_batches] * len(dataloaders)

        self.max_batches = max_batches
        self.num_dataloaders = self._get_num_dataloaders(dataloaders)
        self._predictions = [[] for _ in range(self.num_dataloaders)]

        self.trainer._progress_bar_callback.on_predict_start(self.trainer, self.trainer.get_model())

    def _get_num_dataloaders(self, dataloaders):
        # case where user does:
        # return dl1, dl2
        length = len(dataloaders)
        if len(dataloaders) > 0 and isinstance(dataloaders[0], (list, tuple)):
            length = len(dataloaders[0])
        return length

    def predict(self, batch, batch_idx, dataloader_idx):
        # configure args
        args = [batch, batch_idx]
        if self.num_dataloaders:
            args.append(dataloader_idx)

        model_ref = self.trainer.get_model()

        model_ref._current_fx_name = "predict"
        predictions = self.trainer.accelerator_backend.predict(args)
        self._predictions[dataloader_idx].append(predictions)
        self.trainer._progress_bar_callback.on_predict_batch_end(
            self.trainer, model_ref, predictions, batch, batch_idx, dataloader_idx
        )
        return

    def on_predict_epoch_end(self):
        self.trainer._progress_bar_callback.on_predict_end(self.trainer, self.trainer.get_model())

        results = self._predictions

        def _convert_to_numpy(v):
            return v.cpu().numpy()

        results = apply_to_collection(results, torch.Tensor, _convert_to_numpy)

        if len(results) == 1:
            return results[0]

        return results