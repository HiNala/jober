"use client";

import {
  CartesianGrid,
  Line,
  LineChart as RechartsLineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartAccessibleFigure } from "./chart-accessible";
import { chartColors, chartMargin } from "./chart-theme";

export function AnalyticsLineChart({
  data,
  xKey,
  yKey,
  label,
}: {
  data: Array<Record<string, string | number>>;
  xKey: string;
  yKey: string;
  label: string;
}) {
  if (data.length === 0) {
    return <p className="text-sm text-muted-foreground">No data in this range.</p>;
  }
  return (
    <ChartAccessibleFigure label={label} data={data} xKey={xKey} yKey={yKey}>
    <div className="h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsLineChart data={data} margin={chartMargin}>
          <CartesianGrid stroke={chartColors.grid} vertical={false} />
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 11, fill: chartColors.muted }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: chartColors.muted }}
            tickLine={false}
            axisLine={false}
            width={36}
          />
          <Tooltip
            contentStyle={{
              background: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: 6,
              fontSize: 12,
            }}
          />
          <Line
            type="monotone"
            dataKey={yKey}
            name={label}
            stroke={chartColors.primary}
            strokeWidth={2}
            dot={false}
          />
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
    </ChartAccessibleFigure>
  );
}
