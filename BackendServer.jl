using Oxygen
using HTTP

include("MCTS.jl")

game_count = 0
game_pool = Dict()

mutable struct Game
    id::Int64
    state::HexState
    ai::MCTS
    function Game()
        state = HexState(copy(empty_board),1)
        global game_count += 1
        game = new(game_count,state,MCTS())
        @info "Create Game[id=$(game.id)]"
        game_pool[game_count] = game
        return game
    end
end

function take_action!(game::Game, action::Action)
    game.state = take_action(game.state, action)
end

function kill!(game::Game)
    @info "Delete Game[id=$(game.id)]"
    delete!(game_pool,game.id)
end

function play(game::Game, action::Action)
    @info "Player played at $action)"
    take_action!(game, action)
    winner, gameover = check(game.state.board, action)
    if gameover
        @info "Gameover, Winner: $winner"
        kill!(game)
        return Dict("gameover" => true, "winner" => winner)
    end
    action, detail = search!(game.ai, game.state, action)
    @info "AI played at $action"
    @debug "AI search detail: $detail"
    take_action!(game, action)
    winner, gameover = check(game.state.board, action)
    if gameover
        @info "Gameover Winner: $winner"
        kill!(game)
    end
    return Dict("gameover" => gameover, "winner" => winner, "action" => collect(action))
end

@post "/play" function(req::HTTP.Request)
    data = json(req)
    if haskey(data, "id") && haskey(game_pool, data["id"])
        game = game_pool[data["id"]]
        return play(game, tuple(data["action"]...))
    end
    return Dict("msg" => "Error.")
end

@post "/new" function(req::HTTP.Request)
    data = json(req)
    game = Game()
    if data["you_are_black"]
        action = (6,6)
        game.state = take_action(game.state, action)
        return Dict("id" => game.id, "gameover" => false, "action" => collect(action))
    end
    Dict("id" => game.id, "gameover" => false)
end

# # start the web server
serve()
