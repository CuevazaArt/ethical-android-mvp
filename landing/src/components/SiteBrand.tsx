import Image from "next/image";
import Link from "next/link";

type SiteBrandProps = {
  className?: string;
  showWordmark?: boolean;
};

export function SiteBrand({
  className = "",
  showWordmark = true,
}: SiteBrandProps) {
  return (
    <Link
      href="/"
      className={`flex items-center gap-2.5 md:gap-3 ${className}`}
    >
      <Image
        src="/logo-ethical-awareness.png"
        alt="Mosex Macchina Lab — ethical awareness (cloud, mind, heart)"
        width={44}
        height={44}
        className="h-9 w-9 shrink-0 object-contain md:h-11 md:w-11"
        priority
      />
      {showWordmark ? (
        <span className="text-sm font-medium tracking-tight text-zinc-300">
          Mosex Macchina Lab
        </span>
      ) : null}
    </Link>
  );
}
