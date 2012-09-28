/*
# Plugin Comments
# Framework: Python Web2py (www.web2py.com)
#
# Copyright (c) 2010- Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
# License Code: BSD
# License Content: Creative Commons Attribution 3.0 
#
# Copyright (c) 2011, Martin Mulone
# All rights reserved. 
#
 */
function Exists(element) {	
if (element.length == 0) {
	return false;
}
else {
	return true;
}				
};  
function ShowReplyBox(idreply) {	
	var replyform = '.replyform';
	var replycomment = '#comments #comment-' + idreply;
	var idresponse = '#plugin_comments_comments_reply_id';
	jQuery(replyform).insertAfter(replycomment);
	jQuery(replycomment).insertBefore(replyform);
	jQuery(idresponse).val(idreply);	
};
function ShowBoxContent(id_comment, id_parent) {			
	
	DisplayBox = jQuery("#displaybox");
	ParentBox = jQuery("#comments #comment-" + id_parent);			
	DisplayBox.remove();
	if (!Exists(DisplayBox)) {		
		jQuery('<div id="displaybox"><img src="' + plg_comments_static + 'close.png" class="close" alt="close" title="Close this window" /><div id="displaybox_content"></div></div><div style="clear: both;"></div> ').insertAfter(ParentBox);
		DisplayBox = jQuery("#displaybox");
		DisplayBoxContent = jQuery("#displaybox_content");
		DisplayBoxClose = jQuery("#displaybox .close");
		DisplayBoxClose.click(function(){DisplayBox.remove();}).hover(function(){
			DisplayBoxClose.css({cursor: 'pointer'});
			}, function(){DisplayBoxClose.css({cursor: 'default'});});					
	}
	jQuery.get(plg_comments_showcomment + '/' + id_comment, function(data) {
		DisplayBoxContent.html(data);
	      });
	
	if (DisplayBox.is(":hidden")) {DisplayBox.fadeIn("slow");} else {DisplayBox.remove(); }		
	
};