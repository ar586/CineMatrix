import type { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Register',
    description: 'Create a CineMatrix account to get personalized movie insights.',
};

export default function RegisterLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
