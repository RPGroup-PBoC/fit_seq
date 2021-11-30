using CSV, DataFrames, StanSample, CairoMakie, Jedi, Colors, Statistics, StatsBase

CairoMakie.activate!()
# Set Style
Jedi.styles.default_makie!()

##
# Find home directory
dir = @__DIR__
home_dir = joinpath(split(dir, '/')[1:end-4]...)

# Find date
workdir = split(dir, '/')[end]
DATE = parse(Int64, split(workdir, '_')[1])
RUN_NO = parse(Int64, split(workdir, '_')[2][end])
##

# Read output
data_df = CSV.read("$dir/output/$(DATE)_r$(RUN_NO)_growth_plate.csv", DataFrame)

# Import Stan file
gp_stan = open("/$home_dir/fit_seq/stan_code/gp_growth_rate_prior_deriv.stan") do file
    read(file, String)
end

exp_stan = open("/$home_dir/fit_seq/stan_code/exponential_model.stan") do file
    read(file, String)
end
##
# Compile stan code
println("Compiling Stan files...")
if ~isdir("$dir/stan")
    mkdir("$dir/stan")
end
sm_gp = SampleModel("gaussian_process", gp_stan, "$dir/stan")
sm_exp = SampleModel("exponential_growth", exp_stan, "$dir/stan")


function run_stan_gp(x, y, sm)
    # Set data dictionary
    data = Dict(
        "N" => length(x),
        "t"=> x,
        "y"=> y, 
        "N_predict"=> length(x),  
        "t_predict"=> x, 
        "alpha_param"=> [0, 1], 
        "sigma_param"=> [0, 1], 
        "rho_param"=> [0, 500], 
    )

    # Run stan
    stan_sample(sm; data, num_chains=4);
    # Import results
    df = read_samples(sm, :dataframe)
    # Run summary
    stan_summary(sm)
    # Import summary
    summary = read_summary(sm)
    return df, summary
end


function run_stan_exp(x, y, sm)
    data = Dict(
        "N" => length(x),
        "t"=> x,
        "y"=> log.(y),
        "N_ppc"=> length(x),  
        "t_ppc"=> x
    )

    # Run stan
    stan_sample(sm; data, num_chains=4);
    # Import results
    df = read_samples(sm, :dataframe)
    # Run summary
    stan_summary(sm)
    # Import summary
    summary = read_summary(sm)
    return df, summary
end


function plot_samples_gp(df, data, fig, i, title=nothing)
    # Extract variable names
    y_gp = filter(x -> String(x)[1] == 'y', names(df))
    dy_gp = filter(x -> String(x)[1:2] == "dy", names(df))

    # Prepare axes
    ax1 = Axis(fig[i, 1])
    ax1.xlabel = "time [min]"
    ax1.ylabel = "OD 600"

    ax2 = Axis(fig[i, 2])
    ax2.xlabel = "time [min]"
    ax2.ylabel = "d/dt OD600"

    if ~isnothing(title)
        ax1.title = title
    end
    ax1 = Jedi.viz.predictive_regression(
        [df[!, x] for x in y_gp],
        data[1],
        ax1,
        data=data
        )

    ax2 = Jedi.viz.predictive_regression(
        [df[!, x] for x in dy_gp],
        data[1],
        ax2,
        )
        
    return fig
end


function plot_samples_exp(df, data, fig, i, title=nothing)
    # Extract variable names
    y_ppc = filter(x -> occursin("y_ppc", String(x)), names(df))

    # Prepare axes
    ax1 = Axis(fig[i, 1])
    ax1.xlabel = "time [min]"
    ax1.ylabel = "OD 600"

    if ~isnothing(title)
        ax1.title = title
    end
    ax1 = Jedi.viz.predictive_regression(
        [df[!, x] for x in y_ppc],
        data[1],
        ax1,
        data=data
        )
        
    return fig
end


function analyze_plate(data_df::DataFrames.DataFrame)
    # Get wells
    wells = data_df.well |> unique
    #wells = wells[[1, 50]]

    # Define plotting canvas
    fig_gp = Figure(resolution=(600, 300*length(wells)))
    fig_exp = Figure(resolution=(300, 300*length(wells)))

    # Define DataFrames
    return_df = DataFrames.DataFrame()
    return_sum_df = DataFrames.DataFrame()

    println("Analyzing data...")
    for (i, well) in enumerate(wells)
        println(" Running well $well...")
        # Choosing data for well
        sub_df = data_df[data_df.well .== well, :]
        x = sub_df[!, "time_min"]
        y = sub_df[!, "OD600"]

        println("  Running Gaussian Process...")
        # Run Gaussian process
        df_gp, sum_gp = run_stan_gp(x, y, sm_gp)
        if sum_gp[sum_gp.parameters .== :divergent__, "mean"][1] != 0
            println("There were divergences! $(sum_gp[sum_gp.parameters .== :divergent__, "mean"][1])")
        end
        
        # Find columns with predictions
        y_gp = filter(x -> String(x)[1] == 'y', names(df_gp))
        dy_gp = filter(x -> String(x)[1:2] == "dy", names(df_gp))

        # Compute mean and variance of each step
        mean_y = mean.(eachcol(df_gp[!, y_gp])) 
        mean_dy = mean.(eachcol(df_gp[!, dy_gp]))
        var_y = var.(eachcol(df_gp[!, y_gp])) 
        var_dy = var.(eachcol(df_gp[!, dy_gp])) 

        # Compute maximum growth rate
        lambda_max = maximum(mean_dy ./ mean_y)

        # Add information to dataframe
        insertcols!(
            sub_df, 
            :mean_OD_gp=>mean_y,
            :var_OD_gp=>var_y,
            :mean_lambda_gp=>mean_dy,
            :var_lambda_gp=>var_dy,
        )
        append!(return_df, sub_df)

        # Create dataframe for maximum growth rate
        _df = DataFrames.DataFrame(
            strain=sub_df.strain |> unique, 
            pos_selection=sub_df.pos_selection |> unique, 
            #neg_selection=sub_df.neg_selection |> unique,
            well=well,
            lambda_max=lambda_max,
        )
        
        
        # Run Exponential model
        println("  Running Exponential Growth Model...")

        ind1 = findfirst(x -> x > 0.1, y)
        ind2 = findfirst(x -> x > 0.4, y)
        x_exp = x[ind1:ind2]
        y_exp = y[ind1:ind2]
        df_exp, summary_exp = run_stan_exp(x_exp, y_exp, sm_exp)
        if summary_exp[summary_exp.parameters .== :divergent__, "mean"][1] != 0
            println("There were divergences! $(summary_exp[summary_exp.parameters .== :divergent__, "mean"][1])")
        end

        insertcols!(
            _df, 
            :exp_growth_rate=>mean(df_exp[!, "lambda"]),
        )
        append!(return_sum_df, _df)
        fig_gp = plot_samples_gp(df_gp, [x, y], fig_gp, i, "Gaussian Process: $well")
        fig_exp = plot_samples_exp(df_exp, [x_exp, y_exp], fig_exp, i, "Exponential Growth: $well")
    end
    return return_df, return_sum_df, fig_gp, fig_exp

end

return_df, return_sum_df, fig_gp, fig_exp = analyze_plate(data_df)

CSV.write("$dir/output/gp_analysis.csv", return_df)
CSV.write("$dir/output/gp_analysis_summary.csv", return_sum_df)
save("$dir/output/gp_analysis.pdf", fig_gp)
save("$dir/output/exp_model_analysis.pdf", fig_exp)
println("Done!")
