using Interact, Jedi, CairoMakie, CSV, DataFrames, Dates, ColorSchemes, Statistics

Jedi.styles.default_makie!()

##
dir = @__DIR__
home_dir = joinpath(split(dir, '/')[1:end-4]...)

# Find date
workdir = split(dir, '/')[end]
DATE = parse(Int64, split(workdir, '_')[1])
RUN_NO = parse(Int64, split(workdir, '_')[2][end])
##

# Read output
data_df = CSV.read("$dir/output/$(DATE)_r$(RUN_NO)_growth_plate.csv", DataFrame)

df = DataFrames.DataFrame()

fig = Figure()
ax1 = Axis(fig[1, 1])
ax1.xlabel = "time [min]"
ax1.ylabel = "normalized OD600"

ColorSchemes.seaborn_colorblind

for (strain, color) in zip(data_df.strain |> unique, ColorSchemes.seaborn_colorblind)
    sub_df = data_df[data_df.strain .== strain, :]
    gdf = groupby(sub_df, :time_min)
    mean_df = combine(gdf, :OD600_norm => (x -> (OD_mean=mean(x), OD_std=std(x))) => AsTable)
    insertcols!(mean_df, "strain"=>strain)
    append!(df, mean_df)
    lines!(ax1, mean_df.time_min, mean_df.OD_mean, label=strain)
    scatter!(ax1, mean_df.time_min, mean_df.OD_mean)
    errorbars!(ax1, mean_df.time_min, mean_df.OD_mean, mean_df.OD_std)
end


axislegend(ax1, position=:lt)#, merge = merge, unique = unique)
fig
save("$dir/output/$(DATE)_r$(RUN_NO)_all_curves.pdf", fig)
##
# Read summary output
sum_df = CSV.read("$dir/output/gp_analysis_summary.csv", DataFrame)
fig = Figure(resolution=(300,300))
ax = Axis(fig[1, 1])
scatter!(ax, sum_df.lambda_max, sum_df.exp_growth_rate)
ax.xlabel = "Gaussian Process Growth Rate [1/min]"
ax.ylabel = "Exponential Growth Rate [1/min]"
MIN = minimum(hcat(sum_df.lambda_max, sum_df.exp_growth_rate))
MAX = maximum(hcat(sum_df.lambda_max, sum_df.exp_growth_rate))
lines!(ax, [MIN, MAX], [MIN, MAX])
fig

##
fig = Figure(resolution=(600,300))
ax_min = Axis(fig[1, 1])
ax_supp = Axis(fig[1, 2])

ax_min.xticks = ([1,2], ["Gaussian Process", "Exponential Growth"])
ax_supp.xticks = ([1,2], ["Gaussian Process", "Exponential Growth"])

ax_min.title = "Minimal Medium"
ax_supp.title = "Minimal Medium with supplements"




blue = ColorSchemes.seaborn_colorblind[1]
orange = ColorSchemes.seaborn_colorblind[2]
for i in 1:3

    strain_min = "MG1655_$i"
    strain_supp = "MG1655_supp_$i"
    y1_min = sum_df[sum_df.strain .== strain_min, "lambda_max"]
    y2_min = sum_df[sum_df.strain .== strain_min, "exp_growth_rate"]
    y1_supp = sum_df[sum_df.strain .== strain_supp, "lambda_max"]
    y2_supp = sum_df[sum_df.strain .== strain_supp, "exp_growth_rate"]

    scatter!(ax_min, ones(length(y1_min)) .+randn(length(y1_min))./10 , y1_min, color=blue)
    scatter!(ax_min, ones(length(y2_min)) .* 2 .+randn(length(y1_min))./10, y2_min, color=orange)
    scatter!(ax_supp, ones(length(y1_supp)) .+randn(length(y1_min))./10, y1_supp, color=blue)
    scatter!(ax_supp, ones(length(y2_supp)) .* 2 .+randn(length(y1_min))./10, y2_supp, color=orange)

    
end
ylims!(ax_min, (0.006, 0.009))
ylims!(ax_supp, (0.006, 0.009))
fig
save("$dir/output/growth_rate_comparison.pdf", fig)
