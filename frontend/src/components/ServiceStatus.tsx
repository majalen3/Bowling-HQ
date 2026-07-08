type ServiceStatusProps = {
  label: string;
  value: string;
};

export function ServiceStatus({ label, value }: ServiceStatusProps) {
  return (
    <li>
      <strong>{label}:</strong> {value}
    </li>
  );
}
