# Tweet.nvim
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)  
A simple Neovim remote plugin for Twitter written in Python3

===

## Equipments
- Python3
- pip3

## Installation
vim-plug
``` sh
Plug 'lycoris0731/tweet.nvim', { 'do': 'make' }
```

`make` is executed when install this plugin.  
Then, tweet.nvim install dependency packages using by pip3.  

## Setup
You have to set some environment variables before use this.  
You can register Twitter Apps from [https://apps.twitter.com/](https://apps.twitter.com/).  
``` sh
export TWEET_NVIM_CONSUMER=''
export TWEET_NVIM_CONSUMER_SECRET=''
export TWEET_NVIM_ACCESS_TOKEN=''
export TWEET_NVIM_ACCESS_TOKEN_PRIVATE=''
```

## Usage 
Do tweet based on arguments.  
Each lines are separated by breaks.
``` 
:Tweet [line...]
```



## License
Please see LICENSE.
