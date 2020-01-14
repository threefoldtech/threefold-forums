require "base64"
require 'securerandom'
require 'net/http'
require 'json'

require 'rbnacl'

class ThreebotController < ApplicationController

  skip_before_action :check_xhr, only: [:login]
  skip_before_action :check_xhr, only: [:callback]
  helper_method :sign_in

   @@authUrl = 'https://login.threefold.me'

 def login

    net = Net::HTTP.new("127.0.0.1", 5000)
    net.use_ssl = false
    res = net.get("/pub_key")
    if res.code != "200"
        return render json: {"message": "can not get pelleptic ublic key for this app"}, status: res.code
    end
    data = JSON.load(res.body)
    pk = data['pk']
    state = data['state']
    defaultParams = {
        :appid => '127.0.0.1:9292', #request.host_with_port,
        :scope => JSON.generate({:user=> true, :email => true}),
        :publickey => pk,
        :redirecturl => '/threebot/callback',
        :state => state
    }
    session[:authState] = defaultParams[:state]
    redirect_to "#{@@authUrl}?#{defaultParams.to_query}"
  end

 def callback
    err = params[:error]
    if err == "CancelledByUser"
        Rails.logger.warn 'Login attempt canceled by user'
        return render json: {"message": "Login cancelled by user"}, status: 400
    end
    data = JSON.load(params[:data])
    net = Net::HTTP.new("127.0.0.1", 5000)
    net.use_ssl = false
    res = net.get("/data?#{request.query_parameters.to_query}")

    if res.code != "200"
        return render json: JSON.load(res.body), status: res.code
    end

    data = JSON.load(res.body)

    current_user ||= User.find(session[:user_id]) if session[:user_id]

    if !current_user.nil?
      redirect_to "/" + current_user.username
      return
    end

      user = User.find_by_email(data["email"])
      if user
          session[:user_id] = user.id
          log_on_user(user)
          @current_user = user
       else
        # create new user
        user = User.new(email: data["email"])
        user.password = 'password123456yttt'
        user.username = params[:username].chomp(".3bot")
        user.name = params[:username].chomp(".3bot")
        user.save()
        log_on_user(user)
        @current_user = user
        session[:user_id] = user.id
      end
    redirect_to "/"
  end
end
