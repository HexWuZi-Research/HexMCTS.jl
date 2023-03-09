import Base
using LinearAlgebra

empty_board = zeros(Int64, 11, 11)
for i in 1:6
    empty_board[i, 12-(6-i):end] .= 10
    empty_board[12-i, 1:6-i] .= 10
end

Action = Tuple{Int64,Int64}

struct HexState
    board::Matrix{Int64}
    player::Int64
end

function check_single(line::Vector{Int64})
    L = length(line)
    for i in 1:(L-4)
        player = line[i]
        if player != 0 && player == line[i+1] == line[i+2] == line[i+3] == line[i+4]
            if (i == 1 || line[i-1] != player) && (i == L - 4 || line[i+5] != player)
                return player
            end
        end
    end
    return 0
end

function check_adjacent(board::Matrix{Int64}, pos::Action)
    x, y = pos
    if x != 1 && board[x-1, y] in (-1, 1)
        return true
    end
    if y != 1 && board[x, y-1] in (-1, 1)
        return true
    end
    if x != 1 && y != 1 && board[x-1, y-1] in (-1, 1)
        return true
    end
    if y != 11 && board[x, y+1] in (-1, 1)
        return true
    end
    if x != 11 && board[x+1, y] in (-1, 1)
        return true
    end
    if x != 11 && y != 11 && board[x+1, y+1] in (-1, 1)
        return true
    end
    return false
end

function check_adjacent2(board::Matrix{Int64}, pos::Action)
    if check_adjacent(board, pos)
        return true
    end
    x, y = pos
    if x > 2 && board[x-2, y] in (-1, 1)
        return true
    end
    if y > 2 && board[x, y-2] in (-1, 1)
        return true
    end
    if x > 2 && y > 2 && board[x-2, y-2] in (-1, 1)
        return true
    end
    if y < 10 && board[x, y+2] in (-1, 1)
        return true
    end
    if x < 10 && board[x+2, y] in (-1, 1)
        return true
    end
    if x < 10 && y < 10 && board[x+2, y+2] in (-1, 1)
        return true
    end
    return false
end

function check(board::Matrix{Int64}, action::Union{Action,Nothing}=nothing)
    if action === nothing
        # check if anybody win
        for i in 1:6
            winner = check_single(board[i, 1:i+5])
            if winner != 0
                return winner, true
            end
            winner = check_single(board[1:i+5, i])
            if winner != 0
                return winner, true
            end
        end
        for i in 7:11
            winner = check_single(board[i, i-5:11])
            if winner != 0
                return winner, true
            end
            winner = check_single(board[i-5:11, i])
            if winner != 0
                return winner, true
            end
        end
        for k in -5:5
            winner = check_single(diag(board, k))
            if winner != 0
                return winner, true
            end
        end
    else
        i, j = action
        winner = check_single(i <= 6 ? board[i, 1:i+5] : board[i, i-5:11])
        if winner != 0
            return winner, true
        end
        winner = check_single(j <= 6 ? board[1:j+5, j] : board[j-5:11, j])
        if winner != 0
            return winner, true
        end
        winner = check_single(diag(board, j - i))
        if winner != 0
            return winner, true
        end
    end
    # check if terminated when nobody win
    if 0 ∉ board
        return 0, true
    end
    return 0, false
end

function get_actions(state::HexState)
    actions = Action[]
    for i in 1:6
        for j in 1:i+5
            if state.board[i, j] == 0 && check_adjacent2(state.board, (i, j))
                push!(actions, (i, j))
            end
        end
    end
    for i in 7:11
        for j in i-5:11
            if state.board[i, j] == 0 && check_adjacent2(state.board, (i, j))
                push!(actions, (i, j))
            end
        end
    end
    return actions
end

function take_action(state::HexState, action::Action)
    i, j = action
    board = copy(state.board)
    board[i, j] = state.player
    return HexState(board, -state.player)
end

function is_terminal(state::HexState, action::Union{Action,Nothing}=nothing)
    winner, gameover = check(state.board, action)
    return gameover, winner
end

depth_reward(winner::Int64, board::Matrix{Int64}) = winner * 91 / (count(!=(0), board) - 30)

function random_rollout(state::HexState)
    action = nothing
    while true
        gameover, winner = is_terminal(state, action)
        if gameover
            return depth_reward(winner, state.board)
            # return float(winner)
        end
        action = rand(get_actions(state))
        state = take_action(state, action)
    end
end

mutable struct TreeNode
    state::HexState
    terminal::Bool
    parent::Union{TreeNode,Nothing}
    nvisit::Int64
    reward::Float64
    untried_actions::Vector{Action}
    children::Dict{Action,TreeNode}
    function TreeNode(state::HexState, parent::Union{TreeNode,Nothing}=nothing, action::Union{Action,Nothing}=nothing)
        new(state, is_terminal(state, action)[1], parent, 0, 0.0, get_actions(state), Dict{Action,TreeNode}())
    end
end

Base.show(io::IO, x::TreeNode) = print(io, "TreeNode[state=$(x.state),terminal=$(x.terminal),nvisit=$(x.nvisit),reward=$(x.reward)]")


function uct(child::TreeNode, T::Float64)
    parent = child.parent
    return parent.state.player * child.reward / child.nvisit + T * sqrt(2 * log(parent.nvisit) / child.nvisit)
end

function find_best_action(node::TreeNode, T::Float64)
    best_value = -Inf
    best_actions = Action[]
    for (action, child) in node.children
        value = uct(child, T)
        if value > best_value
            best_value = value
            best_actions = [action]
        elseif value == best_value
            push!(best_actions, action)
        end
    end
    return rand(best_actions)
end

find_best_child(node::TreeNode, T::Float64) = node.children[find_best_action(node, T)]

function select(node::TreeNode, T::Float64)
    while !node.terminal
        # actions is empty, then it's full expanded, then find the best child
        if isempty(node.untried_actions)
            node = find_best_child(node, T)
        else
            return node
        end
    end
    return node
end

function expand!(node::TreeNode)
    action = pop!(node.untried_actions)
    child = TreeNode(take_action(node.state, action), node, action)
    if child.terminal
        node.children = Dict(action => child)
        node.untried_actions = Action[]
    else
        node.children[action] = child
    end
    return child
end

function backpropogate!(node::TreeNode, reward::Float64)
    while node !== nothing
        node.nvisit += 1
        node.reward += reward
        node = node.parent
    end
end

mutable struct MCTS
    time_limit::Real
    T::Float64
    rollout::Function
    root::Union{TreeNode,Nothing}
    our_action::Union{Action,Nothing}
    function MCTS(; time_limit::Real=5, T::Float64=1 / √2, rollout_method::Function=random_rollout)
        new(time_limit, T, rollout_method, nothing, nothing)
    end
end

function round!(self::MCTS)
    node = select(self.root, self.T)
    if !node.terminal
        node = expand!(node)
    end
    reward = self.rollout(node.state)
    backpropogate!(node, reward)
end

function search!(self::MCTS, state::HexState, enemy_action::Union{Action,Nothing}=nothing; need_details=false)
    inherited = false
    # ! try to utilize existed node in the tree
    if enemy_action !== nothing && self.root !== nothing
        node = self.root.children[self.our_action]
        if haskey(node.children, enemy_action)
            node = node.children[enemy_action]
            node.parent = nothing
            inherited = true
        end
    end
    self.root = inherited ? node : TreeNode(state, nothing, nothing)
    excuted_times = 0
    time_limit = time() + self.time_limit
    while time() < time_limit
        round!(self)
        excuted_times += 1
    end
    self.our_action = find_best_action(self.root, 0.0)
    if need_details
        best_child = self.root.children[self.our_action]
        return self.our_action, Dict(
            "use_existed_node" => inherited,
            "expected_reward" => best_child.reward / best_child.nvisit,
            "excuted_times" => excuted_times,
            "root" => self.root
        )
    else
        return self.our_action
    end
end