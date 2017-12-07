Emergency Response System (ERS) simualtor gym environment

To install,

```bash
git clone https://github.com/bhatiaabhinav/gym-ERSLE.git
cd gym-ERSLE
pip install -e .
```

Avaliable environments:

discrete action and discrete state space:
pyERSEnv{di}-v3

continuous action and discrete state space:
pyERSEnv-ca{di}-v3

discrete action and image state space:
pyERSEnv-im{di}-v3

continuous action and image state space:
pyERSEnv-im-ca{di}-v3

where {di} (decision interval in minutes) can be one of {-30, -60, -120, -240, -360, -720, -1440}
omit {di} to set decision interval to 1 min

examples:
pyERSEnv-ca-30-v3, pyERSEnv-im-ca-v3, pyERSEnv-im-1440-v3, pyERSEnv-v3, pyERSEnv-60-v3