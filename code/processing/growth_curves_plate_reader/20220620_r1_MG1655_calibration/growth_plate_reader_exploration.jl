using CairoMakie, CSV, DataFrames, Dates, ColorSchemes, Statistics


##
dir = @__DIR__
home_dir = joinpath(split(dir, '/')[1:end-4]...)

# Find date
c = split(dir, '/')[end]
DATE = parse(Int64, split(workdir, '_')[1])
RUN_NO = parse(Int64, split(workdir, '_')[2][end])

##


println(workdir)

# Read output
#data_df = CSV.read("$dir/output/$(DATE)_r$(RUN_NO)_growth_plate.csv", DataFrame)
sum_df = CSV.read("$dir/output/gp_analysis_summary.csv", DataFrame)

df = DataFrames.DataFrame()

fig = Figure(resolution=(800, 400 * (data_df.strain |> unique |> length)))


# iterater through strains
for (i, strain) in enumerate(data_df.strain |> unique)
    # Get data from this strain
    sub_df = data_df[data_df.strain .== strain, :]
    # Make subplots
    ax1 = Axis(fig[i, 1])
    ax1.xlabel = "time [min]"
    ax1.ylabel = "normalized OD600"
    ax1.title = "$strain"

    ax2 = Axis(fig[i, 2])
    ax2.xlabel = "time [min]"
    ax2.ylabel = "log normalized OD600"
    # Iterate through drug concentrations
    for (pos_selection, color) in zip(sub_df.pos_selection |> unique, ColorSchemes.seaborn_colorblind)
        # Get data
        sub_sub_df = sub_df[sub_df.pos_selection .== pos_selection, :]
        # Get exponential growth rate
        λ = sum_df[(sum_df.strain .== strain) .& (sum_df.pos_selection .== pos_selection), "exp_growth_rate"][1] 
        # Compute mean OD per time step
        gdf = groupby(sub_sub_df, :time_min)
        mean_df = combine(gdf, :OD600_norm => (x -> (OD_mean=mean(x), OD_std=std(x))) => AsTable)
        insertcols!(mean_df, "strain"=>strain)
        append!(df, mean_df)

        # Find time points where exponential growth rate was computed
        ind1 = findfirst(x->x > exp(-3), mean_df.OD_mean)
        ind2 = findfirst(x->x > exp(-2), mean_df.OD_mean)
        # Compute offset
        b = log(mean_df.OD_mean[ind1]) - λ * mean_df.time_min[ind1]
        log_y_exp = λ .* mean_df.time_min[ind1:ind2] .+ b

        # Plot growth curve on linear scale
        #lines!(ax1, mean_df.time_min, mean_df.OD_mean, label=pos_selection)
        
        scatter!(ax1, mean_df.time_min[ind1:ind2], mean_df.OD_mean[ind1:ind2], markersize=2, label=pos_selection)
        lines!(ax1, mean_df.time_min[ind1:ind2], exp.(log_y_exp), linestyle="--", color="white")
        # Plot growth curve on log scale with exponential growth prediction
        #lines!(ax2, mean_df.time_min, log.(mean_df.OD_mean))
        
        scatter!(ax2, mean_df.time_min[ind1:ind2], log.(mean_df.OD_mean)[ind1:ind2], markersize=2)
        lines!(ax2, mean_df.time_min[ind1:ind2], log_y_exp, linestyle="--", color="white")
        errorbars!(ax1, mean_df.time_min, mean_df.OD_mean, mean_df.OD_std)
    end
    axislegend(ax1, position=:lt)#, merge = merge, unique = unique)
end

fig
save("$dir/output/$(DATE)_r$(RUN_NO)_all_curves_with_th.pdf", fig)
##

# Read summary output
sum_df = CSV.read("$dir/output/gp_analysis_summary.csv", DataFrame)

insertcols!(sum_df, 3, :tc => [parse(Float64, split(x, "_")[1]) for x in sum_df[!, "pos_selection"]])

fig = Figure(resolution=(600, 600))
ax1 = Axis(fig[1, 1])#, xscale=log10)
ax2 = Axis(fig[2, 1])#, xscale=log10)

ax1.title = "Exponential Growth Model"
ax2.title = "Gaussian Process"

ax1.xlabel = "tc [µg/ml]"
ax2.xlabel = "tc [µg/ml]"

ax1.ylabel = "λ[1/min]"
ax2.ylabel = "λ[1/min]"

for (i, strain) in enumerate(sum_df.strain |> unique)
    sub_df = sum_df[sum_df.strain .== strain, :]
    scatter!(ax1, sub_df[!, "tc"] , sub_df[!, "exp_growth_rate"], label=strain)
    #scatter!(ax2, sub_df[!, "tc"] , sub_df[!, "lambda_max"], label=strain)
end
axislegend(ax1)#position=:lt)
fig
save("$dir/output/growth_rate_comparison.pdf", fig)
