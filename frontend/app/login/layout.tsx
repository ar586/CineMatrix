import type { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Sign In',
    description: 'Log in to your CineMatrix account to track your favorite movies.',
};

export default function LoginLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
