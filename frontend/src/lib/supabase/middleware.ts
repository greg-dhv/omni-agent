import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          supabaseResponse = NextResponse.next({
            request,
          });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  // Refresh session if expired
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const pathname = request.nextUrl.pathname;

  // Public routes that don't require auth
  const publicRoutes = ['/login', '/callback'];
  const isPublicRoute = publicRoutes.some((route) => pathname.startsWith(route));

  // If not authenticated and trying to access protected route
  if (!user && !isPublicRoute && pathname !== '/') {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }

  // If authenticated, check role-based access
  if (user) {
    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single();

    const isConsultantRoute = pathname.startsWith('/dashboard') ||
      pathname.startsWith('/google-ads') ||
      pathname.startsWith('/seo-content') ||
      pathname.startsWith('/settings');

    const isClientRoute = pathname.startsWith('/reporting') ||
      pathname.startsWith('/actions') ||
      pathname.startsWith('/content');

    // Redirect based on role
    if (profile?.role === 'client' && isConsultantRoute) {
      const url = request.nextUrl.clone();
      url.pathname = '/reporting';
      return NextResponse.redirect(url);
    }

    // Redirect authenticated users from login to appropriate dashboard
    if (pathname === '/login' || pathname === '/') {
      const url = request.nextUrl.clone();
      url.pathname = profile?.role === 'consultant' ? '/dashboard' : '/reporting';
      return NextResponse.redirect(url);
    }
  }

  return supabaseResponse;
}
