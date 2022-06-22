using CSV, DataFrames, StanSample, CairoMakie, Colors, Statistics, StatsBase, fit_seq

CairoMakie.activate!()
fit_seq.plotting_style.default_makie!()
# Set Style
# Find home directory
dir = @__DIR__
home_dir = joinpath(split(dir, '/')[1:end-4]...)

# Find date
workdir = split(dir, '/')[end]
DATE = parse(Int64, split(workdir, '_')[1])
RUN_NO = parse(Int64, split(workdir, '_')[2][end])

# Read output
data_df = CSV.read("$dir/output/$(DATE)_r$(RUN_NO)_growth_plate.csv", DataFrame)

exp_stan = open("/$home_dir/fit_seq/stan_code/exponential_model.stan") do file
    read(file, String)
end

# Compile stan code
println("Compiling Stan files...")
if ~isdir("$dir/stan")
    mkdir("$dir/stan")
end
sm_exp = SampleModel("exponential_growth", exp_stan, "$dir/stan")


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
    df_list = read_samples(sm, :dataframes)
    # Run summary
    stan_summary(sm)
    # Import summary
    summary = read_summary(sm)
    return df_list, summary
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
        data=data,
        data_kwargs=Dict(:markersize => 6)
        )
        
    return fig
end


function analyze_plate(data_df::DataFrames.DataFrame)
    # Get wells
    wells = data_df.well |> unique
    wells = wells

    # Define plotting canvas
    fig_gp = Figure(resolution=(900, 300*length(wells)))
    fig_exp = Figure(resolution=(300, 350*length(wells)))

    # Define DataFrames
    return_df = DataFrames.DataFrame()
    return_sum_df = DataFrames.DataFrame()

    println("Analyzing data...")
    for (i, well) in enumerate(wells)
        println(" Running well $well...")
        # Choosing data for well
        sub_df = data_df[data_df.well .== well, :]
        x = sub_df[!, "time_min"]
        y = sub_df[!, "OD600_norm"]
        
        # Create dataframe for maximum growth rate
        _df = DataFrames.DataFrame(
            strain=sub_df.strain |> unique, 
            pos_selection=sub_df.pos_selection |> unique, 
            well=well,
        )

        # Run Exponential model
        println("  Running Exponential Growth Model...")

        ind1 = findfirst(t -> t > exp(-4), y)
        ind2 = findfirst(t -> t > exp(-2), y)
        x_exp = x[ind1:ind2]
        y_exp = y[ind1:ind2]

        df_exp_list, summary_exp = run_stan_exp(x_exp, y_exp, sm_exp)
        df_exp = vcat(df_exp_list...)

        if summary_exp[summary_exp.parameters .== :divergent__, "mean"][1] != 0
            println("There were divergences! $(summary_exp[summary_exp.parameters .== :divergent__, "mean"][1])")
        end

        insertcols!(
            _df, 
            :exp_growth_rate=>mean(df_exp[!, "lambda"]),
        )
        append!(return_sum_df, _df)

        fig_exp = plot_samples_exp(df_exp, [x_exp, log.(y_exp)], fig_exp, i, "Exponential Growth: $well\n $(sub_df.strain[1])\n $(sub_df.pos_selection[1])")
    end
    return return_sum_df, fig_exp
end

return_sum_df, fig_exp = analyze_plate(data_df)

CSV.write("$dir/output/gp_analysis_summary.csv", return_sum_df)

save("$dir/output/exp_model_analysis.pdf", fig_exp)
println("Done!")
