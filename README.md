<a href="https://www.discourse.org/"><img src=
"https://user-images.githubusercontent.com/1681963/52239617-e2683480-289c-11e9-922b-5da55472e5b4.png"
 width="300px"></a>



3 fold forums is the 100% open source discussion platform built for the next decade of the Internet. [forked from **discourse.org**](https://www.discourse.org)  Use it as a:

- mailing list
- discussion forum
- long-form chat room

To learn more about the philosophy and goals of the project, [visit **discourse.org**](https://www.discourse.org).

## Screenshots


<a href="https://bbs.boingboing.net"><img alt="Boing Boing" src="https://user-images.githubusercontent.com/1681963/52239245-04ad8280-289c-11e9-9c88-8c173d4a0422.png" width="720px"></a>
<a href="https://twittercommunity.com/"><img src="https://user-images.githubusercontent.com/1681963/52239250-04ad8280-289c-11e9-9e42-574f6eaab9d7.png" width="720px"></a>
<a href="https://discuss.howtogeek.com"><img src="https://user-images.githubusercontent.com/1681963/52239247-04ad8280-289c-11e9-9706-fd66bc0749dc.png" width="720px"></a>
<a href="https://talk.turtlerockstudios.com/"><img src="https://user-images.githubusercontent.com/1681963/52239249-04ad8280-289c-11e9-9155-f0ccc5decc50.png" width="720px"></a>

<img src="https://user-images.githubusercontent.com/1681963/52239118-b304f800-289b-11e9-9904-16450680d9ec.jpg" alt="Mobile" width="414">

Browse [lots more notable Discourse instances](https://www.discourse.org/customers).

## Development

To get your environment setup, follow the community setup guide for your operating system.

# Install

- Dev:  cd {src_code}` then `d/boot_dev --init`
- database files are in directory `{src_code}/data` if you want to delete db totally and reiitialize, delete this directory and `docker rm -f discourse_dev`
- 3bot service runs in tmux in user : `discourse`

# RUn
- Dev: `./bin/docker/unicorn`

