require "base64"
require 'securerandom'
require 'net/http'
require 'json'

require 'rbnacl'

class ThreebotController < ApplicationController

  skip_before_action :check_xhr, only: [:login]
  skip_before_action :check_xhr, only: [:callback]
  helper_method :sign_in

   @@authUrl = ENV["THREEBOT_URL"]

 def login
    if !current_user.nil?
      flash[:danger] = "Please log in."
      redirect_to "/"
    end

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
        :appid => request.host_with_port,
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
    net = Net::HTTP.new("127.0.0.1", 5000)
    net.use_ssl = false
    res = net.get("/data?#{request.query_parameters.to_query}")

    if res.code != "200"
        return render json: JSON.load(res.body), status: res.code
    end

    data = JSON.load(res.body)

    user = User.find_by_email(data["email"])

    if user
         user.update_timezone_if_missing(params[:timezone])

        secure_session[UsersController::HONEYPOT_KEY] = nil
        secure_session[UsersController::CHALLENGE_KEY] = nil

        # save user email in session, to show on account-created page
        session[SessionController::ACTIVATE_USER_KEY] = user.id

        # If the user was created as active, they might need to be approved
        user.create_reviewable if user.active?

        user.update_timezone_if_missing(params[:timezone])
        log_on_user(user)
        @current_user = user
        session[:user_id] = user.id
     else

      # create new user
      user = User.new(email: data["email"])
      user.password = 'password123456yttt'
      user.username = data["username"].gsub(".3bot", "")
      user.name = user.username
      user.active = true

      authentication = UserAuthenticator.new(user, session)
      authentication.start
      activation = UserActivator.new(user, request, session, cookies)
      activation.start

      if user.save
        authentication.finish
        activation.finish
        user.update_timezone_if_missing(params[:timezone])

        secure_session[UsersController::HONEYPOT_KEY] = nil
        secure_session[UsersController::CHALLENGE_KEY] = nil

        # save user email in session, to show on account-created page
        session["user_created_message"] = activation.message
        session[SessionController::ACTIVATE_USER_KEY] = user.id

        # If the user was created as active, they might need to be approved
        user.create_reviewable if user.active?

        user.update_timezone_if_missing(params[:timezone])
        log_on_user(user)
        @current_user = user
        session[:user_id] = user.id

       end
    end
    redirect_to "/"
  end
end
