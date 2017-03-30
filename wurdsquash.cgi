#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au April 2011
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/11s1/wordsquash/
# Its a crude implementation which provides some basic features
# You will need to modify and add to this code.
# This codes has bugs & security holes

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use List::Util qw/max/;

sub action_list_blogs();
sub action_display_blog();
sub create_blog();
sub save_posting();
sub markup_to_HTML($);
sub get_html_template($);
sub read_file($);
sub write_file($$);

# This HTML could be in a template file but it assists debugging to have it output ASAP
print header,"<html><head><title>Wurdsquash</title></head><body>\n";
# Leave parameters in a HTML comment for debugging
print "<!-- ".join(",", map({"$_='".param($_)."'"} param()))."-->\n";

my $action = param('action') || 'list_blogs';
my $blog = param('blog') || '';
$blog =~ s/[^a-zA-Z0-9\-]//g;
my %attributes = (
	URL => url(),
	BLOG_HOST_NAME => WordSquash,
	BLOG => $blog,
	BLOG_TITLE => param(new_blog_title) || read_file("$blog.blog_title"),
);

# Possible actions are: list_blogs, new_blog, display_blog, new_posting
# For every action:
# 1) HTML is generated from $action.start.template
# 2) the subroutine action_$action is called if its exists
# 3) HTML is generated from $action.end.template

print get_html_template("templates/$action.start.template");
&{"action_$action"}() if defined &{"action_$action"};
print get_html_template("templates/$action.end.template");
print "</body></html>\n";
exit(0);

# List blogs
sub action_list_blogs() {
	foreach my $blog (sort glob "*.blog_title") {
		($attributes{BLOG} = $blog) =~ s/\.blog_title$//;
		$attributes{BLOG_TITLE} = read_file($blog);
		print get_html_template('templates/list_blogs.blog.template');
	}
}

# Display a blog's contents
sub action_display_blog() {
	create_blog() if defined param(new_blog_title);
	save_posting() if defined param(new_posting_contents);
	foreach $post (sort glob "$blog.*.post") {
		$attributes{POST_TITLE} = read_file("${post}_title");
		$attributes{POST_CONTENT} = markup_to_HTML(read_file($post));
		print get_html_template("templates/display_blog.post.template");
	}
}

sub create_blog() {
	write_file("$blog.blog_title", param(new_blog_title));
}

sub save_posting() {
	my $last_post = max(map(/(\d+).post$/, glob("$blog.*.post")));
	my $file = sprintf "$blog.%d.post", ($last_post || 0) + 1;
	write_file($file, param(new_posting_contents));
	write_file("${file}_title", param(new_posting_title));
}

# convert markup language to HTML
# Markup language is http://en.wikipedia.org/wiki/BBCode 
sub markup_to_HTML($) {
	my ($text) = @_;
	$text =~ s/\[(\/?b)\]/<$1>/g;
	return $text;
}

# read a template and replace any occurences of $identifier with $attributes{$identifier}
sub get_html_template($) {
	my ($file) = @_;
	return "<p><font color=\"red\"><b>MISSING TEMPLATE $file</b></font><p>" if !-r $file;
	my $html = read_file($file);
	$html =~ s/\$(\w+)/defined $attributes{$1} ? $attributes{$1} : "\$$1"/eg;
	return  "<!-- $file begin -->\n$html<!-- $file end -->\n";
}

sub read_file($) {
	my ($file) = @_;
    open(my $f, '<', $file) or return undef;
    return do {local $/; <$f>}
}

sub write_file($$) {
	my ($file, $contents) = @_;
    open my $f, '>', $file or die "Can not write '$file': $!";
    print $f $contents if defined $f;
}
