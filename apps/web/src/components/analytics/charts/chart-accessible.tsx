import type { ReactNode } from "react";

export function ChartAccessibleFigure({
  label,
  data,
  xKey,
  yKey,
  children,
}: {
  label: string;
  data: Array<Record<string, string | number>>;
  xKey: string;
  yKey: string;
  children: ReactNode;
}) {
  return (
    <figure aria-label={label}>
      {children}
      <figcaption className="sr-only">
        <table>
          <thead>
            <tr>
              <th scope="col">{xKey}</th>
              <th scope="col">{yKey}</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={`${row[xKey]}-${index}`}>
                <td>{String(row[xKey])}</td>
                <td>{String(row[yKey])}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </figcaption>
    </figure>
  );
}
