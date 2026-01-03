type Props = { children: React.ReactNode; onClick?: () => void };
export default function PrimaryButton({ children, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="px-6 py-3 rounded-full bg-kidblue text-white font-bold shadow-lg hover:scale-105 transition"
    >
      {children}
    </button>
  );
}
