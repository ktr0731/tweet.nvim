# Tweet.nvim
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)  
[English](./README.md) | [日本語](./README-ja.md)  

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
```
:HomeTimeline
```
Open home timeline.  
If home timeline already opened, fetch latest tweets and show.  

```
:MentionsTimeline
```
Open the timeline about mentions to me.  
If already opened, fetch latest tweets and show.  

```
:ShowLists
```
Show lists.  

```
:Timeline name
```
Open timeline correnponding to `name`.  
If already opened, fetch latest tweets and show.  

``` 
:Tweet [line...]
```
Do tweet based on arguments.  
Each lines are separated by break lines.

```
:Retweet 
```
Do retweet a tweet that on the cursor of Neovim.  

```
:Like
```
Do like a tweet that on the cursor of Neovim.  

```
:Reply [line...]
```
Do reply to a tweet that on the cursor of Neovim.  

## License
Please see LICENSE.
